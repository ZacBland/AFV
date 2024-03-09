import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_lightning.loggers import TensorBoardLogger
from torchvision.models.detection.faster_rcnn import fasterrcnn_mobilenet_v3_large_fpn, FastRCNNPredictor
from utils import collate_fn, bbox_iou  # Ensure this contains any necessary utility functions
import torchvision.transforms as T
from torchvision.datasets import CocoDetection
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
import json
json_file_path = './FLIR_ADAS_v2/images_thermal_train/coco.json'

        # Load the JSON file
with open(json_file_path) as f:
    coco_annotations = json.load(f)

        # Get the number of categories (classes)
num_classes = len(coco_annotations['categories'])

print(f'Number of classes in the dataset: {num_classes}')
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
class DetectionModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        # Load and modify the pre-trained model
        self.model = fasterrcnn_mobilenet_v3_large_fpn(pretrained=True)

        # Path to your COCO format JSON file
        json_file_path = './FLIR_ADAS_v2/images_thermal_train/coco.json'

        # Load the JSON file
        with open(json_file_path) as f:
            coco_annotations = json.load(f)

        # Get the number of categories (classes)
        num_classes = len(coco_annotations['categories'])

        print(f'Number of classes in the dataset: {num_classes}')

        num_classes = num_classes  # COCO dataset has 80 classes; +1 is for the background
        
        # Replace the classifier with a new one, where num_classes is the number of classes
        in_features = self.model.roi_heads.box_predictor.cls_score.in_features
        self.model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    def forward(self, images, targets=None):
        return self.model(images, targets)

    def training_step(self, batch, batch_idx):
        images, targets = batch
        loss_dict = self.model(images, targets)
        loss = sum(loss for loss in loss_dict.values())
        self.log('train_loss', loss)
        return loss

    def validation_step(self, batch, batch_idx):
        images, targets = batch
        images = [image.to(self.device) for image in images]
        outputs = self.model(images)

        # Assuming outputs and targets are lists of dictionaries as expected by PyTorch detection models
        # And that targets and model outputs are in the same order
        ious = []
        for output, target in zip(outputs, targets):
            preds_boxes = output['boxes']
            gt_boxes = target['boxes']
            
            # For simplicity, matching boxes by order. For real scenarios, match boxes based on some criteria like highest IoU.
            for pred_box, gt_box in zip(preds_boxes, gt_boxes):
                iou = bbox_iou(pred_box, gt_box)
                ious.append(iou)

        # Compute mean IoU for the batch
        mean_iou = torch.tensor(ious).mean() if ious else torch.tensor(0)
        self.log('val_iou', mean_iou, on_step=False, on_epoch=True, prog_bar=True)


    def configure_optimizers(self):
        optimizer = torch.optim.SGD(self.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005)
        scheduler = ReduceLROnPlateau(optimizer, 'min')
        return {'optimizer': optimizer, 'lr_scheduler': scheduler, 'monitor': 'val_loss'}

class COCODataModule(pl.LightningDataModule):
    def __init__(self, train_dir, val_dir, test_dir, batch_size=4):
        super().__init__()
        self.train_dir = train_dir
        self.val_dir = val_dir
        self.test_dir = test_dir
        self.batch_size = batch_size
        self.transform = T.Compose([
            T.Resize((640, 512)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def setup(self, stage=None):
        # Load datasets
        if stage == 'fit' or stage is None:
            self.train_dataset = CocoDetection(root=self.train_dir, annFile=f'{self.train_dir}/coco.json', transform=self.transform)
            self.val_dataset = CocoDetection(root=self.val_dir, annFile=f'{self.val_dir}/coco.json', transform=self.transform)
        if stage == 'test' or stage is None:
            self.test_dataset = CocoDetection(root=self.test_dir, annFile=f'{self.test_dir}/coco.json', transform=self.transform)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=4, collate_fn=collate_fn)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=False, num_workers=4, collate_fn=collate_fn)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size, shuffle=False, num_workers=4, collate_fn=collate_fn)
data_module = COCODataModule('./FLIR_ADAS_v2/images_thermal_train', './FLIR_ADAS_v2/images_thermal_val', './FLIR_ADAS_v2/video_thermal_test')
model = DetectionModel()

# Callbacks
checkpoint_callback = ModelCheckpoint(monitor='val_iou', mode='max', save_top_k=1, verbose=True)
early_stop_callback = EarlyStopping(monitor='val_iou', patience=10, verbose=True, mode='max')

# Logger
logger = TensorBoardLogger("tb_logs", name="my_model")

trainer = pl.Trainer(max_epochs=100, accelerator="auto", devices="auto", strategy="auto", callbacks=[checkpoint_callback, early_stop_callback], logger=logger)
trainer.fit(model, datamodule=data_module)
