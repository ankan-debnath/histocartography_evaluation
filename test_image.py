from histocartography.preprocessing import NucleiExtractor, DeepFeatureExtractor, KNNGraphBuilder
import numpy as np
from PIL import Image

nuclei_detector = NucleiExtractor(batch_size=8)
feature_extractor = DeepFeatureExtractor(architecture='resnet34', batch_size=8, patch_size=72)
knn_graph_builder = KNNGraphBuilder(k=5, thresh=50, add_loc_feats=True)

image = np.array(Image.open('demo_HNE.png'))
nuclei_map, _ = nuclei_detector.process(image)
features = feature_extractor.process(image, nuclei_map)
cell_graph = knn_graph_builder.process(nuclei_map, features)


from histocartography.visualization import OverlayGraphVisualization, InstanceImageVisualization

visualizer = OverlayGraphVisualization(
  instance_visualizer=InstanceImageVisualization(
    instance_style="filled+outline"
  )
)
viz_cg = visualizer.process(
  canvas=image,
  graph=cell_graph,
  instance_map=nuclei_map
)
# viz_cg.show()
viz_cg.save('visualized_cell_graph.png')
