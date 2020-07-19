import torch
from torch.utils.data import DataLoader
from object_detection.models.centernetv1 import (
    collate_fn,
    CenterNetV1,
    Visualize,
    Trainer,
    Criterion,
    ToBoxes,
    Anchors,
    MkMaps,
)
from object_detection.models.box_merge import BoxMerge
from object_detection.models.backbones.effnet import EfficientNetBackbone
from object_detection.model_loader import ModelLoader, BestWatcher
from object_detection.data.object import TrainDataset
from object_detection.metrics import MeanPrecition
from . import config as cfg



def train(epochs: int) -> None:
    train_dataset = TrainDataset(
        cfg.input_size,
        object_count_range=cfg.object_count_range,
        object_size_range=cfg.object_size_range,
        num_samples=1024,
    )
    test_dataset = TrainDataset(
        cfg.input_size,
        object_count_range=cfg.object_count_range,
        object_size_range=cfg.object_size_range,
        num_samples=256,
    )
    backbone = EfficientNetBackbone(1, out_channels=cfg.channels, pretrained=True)
    model = CenterNetV1(
        channels=cfg.channels,
        backbone=backbone,
        out_idx=cfg.out_idx,
        box_depth=cfg.box_depth,
        anchors=Anchors(size=cfg.anchor_size),
    )
    mk_maps = MkMaps(sigma=cfg.sigma, mode=cfg.mode)
    criterion = Criterion(
        box_weight=cfg.box_weight, heatmap_weight=cfg.heatmap_weight, mk_maps=mk_maps,
    )
    train_loader = DataLoader(
        train_dataset, collate_fn=collate_fn, batch_size=cfg.batch_size, shuffle=True
    )
    test_loader = DataLoader(
        test_dataset, collate_fn=collate_fn, batch_size=cfg.batch_size * 2, shuffle=True
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr)
    visualize = Visualize(cfg.out_dir, "test", limit=2)

    model_loader = ModelLoader(
        out_dir=cfg.out_dir, key=cfg.metric[0], best_watcher=BestWatcher(mode=cfg.metric[1])
    )
    to_boxes = ToBoxes(threshold=cfg.to_boxes_threshold)
    get_score = MeanPrecition()
    box_merge = BoxMerge(iou_threshold=cfg.iou_threshold)
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        test_loader=test_loader,
        model_loader=model_loader,
        optimizer=optimizer,
        visualize=visualize,
        criterion=criterion,
        box_merge=box_merge,
        device="cuda",
        get_score=get_score,
        to_boxes=to_boxes,
    )
    trainer(epochs)
