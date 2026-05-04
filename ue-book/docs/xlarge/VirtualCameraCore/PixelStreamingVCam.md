# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `VCamCore` (Runtime), `VCamBlueprintNodes` (Runtime), `PixelStreamingVCam` (Runtime), `DecoupledOutputProvider` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

---

## 用途

VirtualCameraCore 是 Unreal Engine 虚拟制片（Virtual Production）管线中的核心插件，提供通过物理设备（如 iPad、iPhone）远程控制和监看虚拟摄像机的完整框架。

该插件解决的核心问题：

1. **远程摄像机控制**：允许用户通过移动设备实时操控 UE 场景中的虚拟摄像机，包括位置、旋转、焦距、光圈等参数
2. **实时视频回传**：通过 Pixel Streaming 技术将摄像机画面实时传输到移动设备上，实现低延迟监看
3. **输出解耦架构**：通过 DecoupledOutputProvider 模块将摄像机输出与具体渲染管线解耦，支持多种输出目标
4. **蓝图集成**：提供蓝图节点，使非程序员也能快速搭建虚拟摄像机工作流

该插件是 Epic Games 虚拟制片工具链的基础设施层，VirtualCamera 插件（内容层）依赖于此插件提供的运行时框架。

## 使用场景

- 你在做虚拟制片项目，需要导演通过 iPad 实时调整虚拟摄像机角度 → 用 VirtualCameraCore
- 你需要将 UE 场景画面通过 Pixel Streaming 低延迟传输到移动设备 → 用 PixelStreamingVCam 模块
- 你需要自定义虚拟摄像机的输出目标（如多屏输出、自定义渲染目标）→ 用 DecoupledOutputProvider 模块
- 你正在开发基于 ARKit 的摄像机追踪应用 → 该插件内置 ARKit transform 支持

## 模块架构

```
VirtualCameraCore/
├── VCamCore/                    ← 核心运行时框架（Actor、Component、工具类）
├── VCamBlueprintNodes/          ← 蓝图节点扩展
├── PixelStreamingVCam/          ← Pixel Streaming 集成（视频回传）
├── DecoupledOutputProvider/     ← 解耦输出提供器架构
└── VCamCoreEditor/              ← 编辑器扩展
```

---

# PixelStreamingVCam 模块

## 用途

PixelStreamingVCam 模块负责将虚拟摄像机的画面通过 Pixel Streaming 技术实时传输到远程设备。它是 VirtualCameraCore 中实现"视频回传"功能的关键模块。

核心职责：
- 管理 Pixel Streaming 会话的生命周期
- 处理媒体捕获（Media Capture）的启停
- 管理 ARKit 追踪数据的变换队列
- 防止在媒体捕获关闭后仍被占用变换控制

## 蓝图用法

由于该模块头文件信息有限，以下为基于源码分析推断的核心功能：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 启动 Pixel Streaming 会话 | 开始将摄像机画面通过 Pixel Streaming 传输 | `UPixelStreamingVCam*` |
| 停止 Pixel Streaming 会话 | 停止传输并清理资源 | `UPixelStreamingVCam*` |
| 设置输出提供器 | 配置解耦输出目标 | `UPixelStreamingVCam*` |

### 使用示例（蓝图描述）

典型的虚拟摄像机 Pixel Streaming 工作流：

1. 在场景中放置 VirtualCamera Actor
2. 添加 PixelStreamingVCam 组件
3. 配置 Pixel Streaming 服务器地址和端口
4. 通过蓝图调用"启动会话"节点
5. 在移动设备上通过浏览器连接查看实时画面
6. 结束时调用"停止会话"节点，确保资源正确释放

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreamingVCam.h"
```

### 基本用法

基于 git commit 分析的典型使用模式：

```cpp
// 启动媒体捕获时的典型处理
// 来源: 882502a6e8f6 - 防止媒体捕获关闭后仍被占用变换控制

void StartVCamCapture()
{
    // 启动 Pixel Streaming 媒体捕获
    // 确保在捕获期间正确管理变换控制权
    if (MediaCapture && !MediaCapture->IsCapturing())
    {
        MediaCapture->StartCapture();
        bIsTransformControlActive = true;
    }
}

void StopVCamCapture()
{
    // 停止捕获并释放变换控制
    if (MediaCapture && MediaCapture->IsCapturing())
    {
        MediaCapture->StopCapture();
        bIsTransformControlActive = false;  // 关键：防止控制权残留
    }
}
```

### 进阶用法

ARKit 追踪数据管理（来源: 8f3832b6faf6）：

```cpp
// 当捕获停止时，清理 ARKit 变换持有者和队列
void OnCaptureStopped()
{
    // 清理 ARKit 追踪数据
    ClearARKitTransformHolder();
    FlushTransformQueue();
    
    // 确保所有待处理的变换数据被正确丢弃
    // 防止下次启动时使用过期数据
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelEditor` | 关卡编辑器集成 |
| `UnrealEd` | 编辑器工具支持 |
| `PixelStreaming` | Pixel Streaming 核心功能（隐式依赖） |
| `MediaCapture` | 媒体捕获框架（隐式依赖） |

## 维护状态

### 近期更新

```
- 882502a6e8f6 [UnrealVCam] Prevent transform control being taken after media capture is shut down
- 8f3832b6faf6 [VCam] Clear ARKit transform holder + queue when capture stops
- 958272d22131 Remove use of the old composure plugin from VPUtilities and VCamCore
```

### 维护评价

- **创建时间**：2023-02-07，约 2 年历史
- **维护状态**：活跃维护中，近期有实质性 bug 修复和架构改进
- **已知限制**：
  - 标记为 `IsBetaVersion: true`，API 可能发生变化
  - `EnabledByDefault: false`，需要手动启用
- **推荐程度**：✅ 推荐用于虚拟制片项目，但需注意 Beta 状态，生产环境使用前充分测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore/Source/PixelStreamingVCam)
- [VirtualCameraCore 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- [官方文档]()（暂无）