# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `VCamCore` (Runtime), `VCamBlueprintNodes` (Runtime), `PixelStreamingVCam` (Runtime), `DecoupledOutputProvider` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

VirtualCameraCore 是一个**底层框架插件**，为构建虚拟摄影机（VCam）系统提供核心运行时逻辑、蓝图接口和编辑器工具。它本身不包含完整的用户界面或内容资产（这些在 `VirtualCamera` 插件中），而是专注于提供可扩展的代码基础，用于：
1.  **抽象化输入设备**：将来自物理设备（如iPad、专业控制器）的输入映射为相机控制指令。
2.  **管理相机状态与输出**：处理相机变换、焦距等参数，并将最终画面输出到各种目标（如视口、像素流）。
3.  **提供蓝图可编程性**：通过蓝图节点暴露核心功能，允许用户在不编写C++的情况下构建自定义的VCam工作流。
4.  **支持像素流**：集成像素流送技术，使远程设备能够实时查看和控制UE相机。

## 使用场景

-   **虚拟制片团队**：需要通过iPad等移动设备实时控制UE场景中的虚拟相机，用于预览或拍摄。
-   **多用户协作**：多个操作员需要同时控制或查看同一场景中的不同相机视角。
-   **自定义VCam工作流**：开发者希望基于此框架，构建具有独特输入逻辑、输出目标或UI界面的专用虚拟摄影机系统。
-   **远程监看与控制**：利用像素流技术，让导演或客户在远离工作站的地方实时参与镜头设计。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| **VCamCore** | Runtime | 核心运行时模块，包含VCam输入处理、相机控制器、输出管理等基础框架。 | [VCamCore.md](VCamCore.md) |
| **VCamBlueprintNodes** | Runtime | 提供蓝图节点，将VCamCore的核心功能暴露给蓝图系统，便于可视化编程。 | [VCamBlueprintNodes.md](VCamBlueprintNodes.md) |
| **PixelStreamingVCam** | Runtime | 集成像素流送功能，支持将VCam画面通过WebRTC流式传输到远程设备。 | [PixelStreamingVCam.md](PixelStreamingVCam.md) |
| **DecoupledOutputProvider** | Runtime | 提供解耦的输出提供者模式，允许将VCam输出灵活地路由到不同的目标。 | [DecoupledOutputProvider.md](DecoupledOutputProvider.md) |
| **VCamCoreEditor** | Runtime | 编辑器扩展模块，提供用于配置和调试VCam系统的编辑器工具和资产类型。 | [VCamCoreEditor.md](VCamCoreEditor.md) |

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore)
-   [官方文档]() (暂无)
-   [测试用例]() (暂无)