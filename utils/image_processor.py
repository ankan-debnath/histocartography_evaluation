from histocartography.preprocessing import (
    NucleiExtractor,
    DeepFeatureExtractor,
    KNNGraphBuilder
)
from histocartography.preprocessing.stain_normalizers import MacenkoStainNormalizer
from PIL import Image
import numpy as np
import os


class Image_Processor:
    def __init__(self, thresh=5):
        # Initialize tools
        self.NUCLEI_THRESHOLD = thresh
        self.stain_normalizer = MacenkoStainNormalizer()
        self.nuclei_detector = NucleiExtractor(batch_size=8)
        self.feature_extractor = DeepFeatureExtractor(architecture='resnet34', batch_size=8, patch_size=72)
        self.knn_graph_builder = KNNGraphBuilder(k=5, thresh=50, add_loc_feats=True)

    def count_nuclei(self, nuclei_map):
        """
        Count distinct nuclei in nuclei_map.
        nuclei_map is typically a labeled segmentation mask:
        each nucleus has a unique integer label > 0, background is 0.
        """

        unique_labels = np.unique(nuclei_map)
        nuclei_count = len(unique_labels) - (1 if 0 in unique_labels else 0)
        return nuclei_count

    def classify_image(self, image_path):
        image = np.array(Image.open(image_path))

        # Ensure 3-channel RGB
        if image is not None and image.ndim == 2:
            image = np.stack([image]*3, axis=-1)


        # Get nuclei segmentation map (nuclei_map) and _ (additional output)
        nuclei_map, _ = self.nuclei_detector.process(image)

        nuclei_count = self.count_nuclei(nuclei_map)
        print(f"Nuclei detected: {nuclei_count}")

        return (
            "non-pathology"
            if nuclei_count < self.NUCLEI_THRESHOLD
            else "pathology"
        )

    def preprocess_image(self, image_path):
        """Load and normalize the image."""
        image = np.array(Image.open(image_path))
        self.stain_normalizer.fit(image)
        norm_image = self.stain_normalizer._process(image)
        return norm_image

    def get_nuclei_graph(self, image):
      nuclei_map, nuclei_info = self.nuclei_detector.process(image)
      features = self.feature_extractor.process(image, nuclei_map)

      n_samples = len(nuclei_info)

      # Case 1: No nuclei detected
      if n_samples == 0:
          return nuclei_map, nuclei_info, None

      # Case 2: Only 1 nucleus detected → graph not possible
      if n_samples == 1:
          return nuclei_map, nuclei_info, None

      # Case 3: Normal case (at least 2 nuclei)
      k = min(self.knn_graph_builder.k, n_samples - 1)  # ensure valid k
      graph_builder = KNNGraphBuilder(k=k, thresh=50, add_loc_feats=True)
      graph = graph_builder.process(nuclei_map, features)

      return nuclei_map, nuclei_info, graph

      
    def divide_into_patches(self, image, patch_rows=3, patch_cols=3, overlap=0.2):
        """Divide the image into overlapping patches."""
        h, w, _ = image.shape
        stride_y = int(h / patch_rows * (1 - overlap))
        stride_x = int(w / patch_cols * (1 - overlap))
        patch_h = stride_y + int(h / patch_rows * overlap)
        patch_w = stride_x + int(w / patch_cols * overlap)

        patches = []
        coords = []
        for i in range(patch_rows):
            for j in range(patch_cols):
                y_start = i * stride_y
                x_start = j * stride_x
                y_end = min(y_start + patch_h, h)
                x_end = min(x_start + patch_w, w)

                patch = image[y_start:y_end, x_start:x_end]
                patches.append(patch)
                coords.append((x_start, y_start, x_end, y_end))
        return patches, coords

    def count_nuclei_in_patch(self, nuclei_info, x0, y0, x1, y1):
        """Count nuclei centers inside a given patch."""
        count = 0
        for nucleus in nuclei_info:
            x, y = nucleus
            if x0 <= x < x1 and y0 <= y < y1:
                count += 1
        return count

    def extract_top_patches(self, image_path, top_k=3):
        """Full pipeline: get top-k patches based on nuclei density."""
        image = self.preprocess_image(image_path)
        nuclei_map, nuclei_info, _ = self.get_nuclei_graph(image)

        patches, coords = self.divide_into_patches(image)

        patch_nuclei_counts = []
        for coord in coords:
            count = self.count_nuclei_in_patch(nuclei_info, *coord)
            patch_nuclei_counts.append(count)

        # Rank patches
        sorted_indices = sorted(range(len(patch_nuclei_counts)), key=lambda i: patch_nuclei_counts[i], reverse=True)
        top_patches = [patches[i] for i in sorted_indices[:top_k]]
        top_coords = [coords[i] for i in sorted_indices[:top_k]]

        return top_patches, top_coords, patch_nuclei_counts

    # Example usage
    def generate_patches(self, image_path, save_dir="temp_uploads"):
        top_patches, coords, counts = self.extract_top_patches(image_path, top_k=3)
        os.makedirs(save_dir, exist_ok=True)

        # Save top patches for verification
        for i, patch in enumerate(top_patches):
            patch_name = f"histo_patch_{i}.png"
            filepath = os.path.join(save_dir, patch_name)
            Image.fromarray(patch).save(filepath)
            print(f"Saved: {filepath}")
