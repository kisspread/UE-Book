# Apple ARKit

> Support for Apple's ARKit augmented reality system

| 属性 | 值 |
|---|---|
| 中文名 | 苹果ARKit支持 |
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AppleARKit` (Runtime), `AppleARKitPoseTrackingLiveLink` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit) | |

## 用途

该插件是 Unreal Engine 5 与苹果 ARKit 框架之间的核心桥梁。它封装并暴露了 ARKit 的高级功能，使 UE5 开发者能够在支持 ARKit 的 iOS 设备（iPhone、iPad）上构建增强现实应用。插件实现了对平面检测、图像追踪、物体追踪、人脸追踪、环境光估计等核心 AR 功能的访问，并将这些数据集成到 UE5 的 XR 系统中。

## 使用场景

- 开发 iOS 平台的 AR 应用，如虚拟试穿、家具摆放预览。
- 创建需要环境理解（如地面、墙面）的互动游戏或体验。
- 利用设备摄像头进行人脸追踪，驱动虚拟角色表情。
- 在工业或培训应用中，将 3D 模型叠加到真实设备或图纸上。

## 模块列表

- **`AppleARKit`**: 核心运行时模块。负责与原生 ARKit 交互，管理 AR 会话生命周期，并将追踪数据（平面、图像、人脸等）转换为 UE5 可用的格式。提供蓝图和 C++ API 供开发者使用。
- **`AppleARKitPoseTrackingLiveLink`**: LiveLink 源模块。专注于从 ARKit 获取人体姿态追踪数据，并通过 LiveLink 框架将其实时传输到其他 Actor 或外部应用程序，用于实时动画驱动或远程预览。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit/Tests)