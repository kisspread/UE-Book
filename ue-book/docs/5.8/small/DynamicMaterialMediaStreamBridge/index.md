# Material Designer Media Stream Bridge

> Integrates the Media Stream plugin with the Material Designer.

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计器媒体流桥接 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产数据） |
| 模块 | `DynamicMaterialMediaStreamBridge` (Runtime), `DynamicMaterialMediaStreamBridgeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge) | |

## 用途

本插件在 UE5 的 `DynamicMaterial`（材质设计器）框架和 `MediaStream`（媒体流）系统之间建立桥梁。它解决的核心问题是：如何将实时媒体流（如视频、摄像头画面）作为纹理输入，无缝地集成到通过材质设计器创建的动态材质实例中，实现实时、可视化的媒体材质创作。

## 使用场景

- 你在使用材质设计器（Material Designer）创建动态材质，并希望将一个媒体播放器（MediaPlayer）的视频输出实时用作材质的纹理。
- 你需要开发一个具有实时视频反馈效果的材质，例如在游戏内显示动态屏幕或监控画面，并希望利用材质设计器的节点化界面进行快速原型设计。
- 你想将 MediaStream 插件提供的媒体资产（如 `UMediaStream`）与材质设计器中代表纹理参数的 `UDMMaterialSlot` 进行关联。

## 蓝图用法

此插件主要为材质设计器提供媒体流支持，其核心逻辑更多体现为资产和数据连接，而非暴露大量独立的蓝图节点。具体的使用方式是通过材质设计器的接口将媒体流资产关联到材质槽位。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （数据连接） | 将 `UMediaStream` 资产连接到材质设计器的纹理参数槽位 | `UDMMaterialSlot` |

### 使用示例（蓝图描述）

在材质设计器的图表中，选中一个代表纹理输入的材质参数槽位（Texture Slot）。在细节面板中，将 `Media Stream` 属性从 `None` 设置为你项目中已创建的某个 `UMediaStream` 资产。这样，该媒体流的输出就会实时渲染到这个材质槽位所代表的纹理上。

## C++ 用法

插件通过运行时和编辑器模块提供底层集成，通常不直接在项目代码中调用，而是被材质设计器和媒体流系统内部使用。若需扩展或自定义集成逻辑，请参考其模块源码。

### 头文件引入

```cpp
#include "DynamicMaterialMediaStreamBridgeModule.h" // 运行时模块头文件
#include "DynamicMaterialMediaStreamBridgeEditorModule.h" // 编辑器模块头文件
```

### 基本用法

插件的核心是注册媒体流作为材质设计器的一种纹理源。此过程由插件内部自动完成。开发者的主要交互点是通过 `UMediaStream` 资产和材质设计器 UI。

## Demo 示例

本插件作为集成层，不提供独立的可运行 Demo。其功能演示体现在将 `UMediaStream` 资产拖拽或指定到材质设计器材质槽位的过程。

## 模块依赖

要使用此插件，你的项目需要启用 `DynamicMaterial` 和 `MediaStream` 这两个插件。你的模块若需访问其类型，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 材质设计器核心框架 |
| `MediaStream` | 媒体流核心框架 |
| `MediaAssets` | 处理媒体播放器等资产 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `82b74724` | [MediaStream] Adding a cache setting override (like MediaPlate does) for using a local cache when us | 为媒体流添加本地缓存设置，提升播放性能。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持共享字符串，优化内存。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的字符串重复，释放内存。 |

### 维护评价

**推荐使用**。插件创建时间较新（约1年），且从提交历史看，近期（2026年）仍在进行活跃的功能增强和优化（如缓存设置、内存优化），表明处于积极维护状态。作为实验性插件，适合在需要实时媒体流材质的设计项目中进行原型开发和内部使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge/Tests) （如果存在）