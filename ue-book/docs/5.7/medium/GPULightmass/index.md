# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照质量 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass) | |

## 📖 总体用途

GPULightmass 利用 DXR（DirectX Raytracing）硬件加速，在编辑器内快速构建和预览静态光照（Lightmass 烘焙效果），大幅缩短传统 Lightmass 的烘焙时间，支持实时调整光照参数并立即看到结果，适用于需要高质量静态光照且需要频繁迭代的游戏或可视化项目。

## 🧩 模块总览

所有子模块的详情请查阅对应文档：

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [GPULightmass](GPULightmass.md) | UncookedOnly | 核心光照计算引擎，负责 DXR 光线追踪、光照图生成与实时预览 |
| [GPULightmassEditor](GPULightmassEditor.md) | Editor | 编辑器集成层，提供 UI 面板、烘焙控制、交互预览与设置管理 |

## 🛠 使用场景

- 你需要快速预览静态光照效果，而不想等待传统 CPU Lightmass 的长时间烘焙
- 场景中光源较多、光照贴图分辨率高，传统烘焙耗时过长
- 需要频繁调整光源位置、颜色或强度，并立即看到烘焙结果
- 硬件支持 DXR（需 Windows 10 / DX12 和兼容 GPU）

## 🔗 相关链接

- [插件源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass)