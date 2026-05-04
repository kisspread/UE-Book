# XRScribe

> OpenXR API Capture/Emulation

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | XRScribe (Runtime, PostConfigInit) |
| 创建时间 | 2023-04-25 |
| 年龄标签 | 🆕 |
| 平台限制 | Win64 |
| 依赖插件 | OpenXR |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/XR/XRScribe) | |

## 用途

XRScribe 是一个 **OpenXR API 录制与回放** 工具。它通过在 OpenXR 运行时之上插入一个 API 层（API Layer），拦截并记录所有 OpenXR API 调用（Capture 模式），然后在没有实际 XR 头显硬件的环境下回放这些调用（Emulate 模式）。

核心价值：**开发者无需连接 VR 头显即可进行 XR 应用的开发和调试**。Capture 录制真实的 OpenXR 交互会话（包括头显姿态、控制器输入、Session 生命周期等），Emulate 则在桌面环境中模拟这些交互，使得非 XR 环境也能运行 XR 逻辑。

该 plugin 的架构灵感来自 OpenXR 的 API Layer 机制——在应用和真实运行时之间插入一个拦截层。

## 使用场景

- 你在开发 VR 应用，但不想每次测试都戴上头显 → Capture 一次真实会话，之后用 Emulate 回放
- 你是一个程序员，需要在 CI/CD 中对 XR 逻辑做自动化测试 → 用 Capture 录制的 `.xrs` 文件作为测试输入
- 你需要录制一段 VR 交互用于 bug 复现 → Capture 模式记录完整的 API 调用序列
- 你在没有 XR 硬件的机器上开发 → 先在有硬件的机器上 Capture，再在开发机上 Emulate

## 蓝图用法

XRScribe 是一个底层基础设施 plugin，**没有暴露任何蓝图节点**。它的所有功能通过编辑器设置（Developer Settings）和配置文件控制，不面向蓝图用户。

## C++ 用法

XRScribe 的主要交互方式是通过 **配置** 而非代码。它作为 OpenXR API Layer 自动拦截所有 OpenXR 调用。

### 配置方式

在 `DefaultEngine.ini` 中配置运行模式：

```ini
[XRScribe]
RunMode=0  ; 0 = Capture (录制), 1 = Emulate (回放/模拟)
```

或通过编辑器设置：**Project Settings → Engine → XRScribe**（`UXRScribeDeveloperSettings`）。

`RunMode` 设置需要重启引擎生效（`ConfigRestartRequired = true`）。

### 头文件引入

```cpp
#include "XRScribeAPISurface.h"    // API 层管理器
#include "XRScribeCaptureLayer.h"  // Capture 层
#include "XRScribeEmulationLayer.h" // Emulation 层
#include "XRScribeFileFormat.h"    // 数据包格式定义
```

### 通过 IOpenXRAPILayerManager 访问

```cpp
#include "XRScribeAPISurface.h"

// 获取 API 层管理器
UE::XRScribe::IOpenXRAPILayerManager& Manager = UE::XRScribe::IOpenXRAPILayerManager::Get();

// 获取当前活跃的层（Capture 或 Emulation）
UE::XRScribe::IOpenXRAPILayer* ActiveLayer = Manager.GetActiveLayer();
```

### 加载 Capture 数据到 Emulation 层

```cpp
#include "XRScribeEmulationLayer.h"

// 从文件加载
UE::XRScribe::FOpenXREmulationLayer* EmulateLayer = /* ... */;
bool bSuccess = EmulateLayer->LoadCaptureFromFile(TEXT("Saved/Capture.xrs"));

// 从内存加载
TArray<uint8> EncodedData;
bool bSuccess = EmulateLayer->LoadCaptureFromData(EncodedData);
```

### 自定义 API 层继承

如果需要扩展，可以继承 `IOpenXRAPILayer` 接口：

```cpp
#include "XRScribeAPILayer.h"

class FMyCustomLayer : public UE::XRScribe::IOpenXRAPILayer
{
public:
    virtual bool SupportsInstanceExtension(const ANSICHAR* ExtensionName) override;
    virtual XrResult XrLayerCreateInstance(const XrInstanceCreateInfo* createInfo, XrInstance* instance) override;
    // ... 实现所有纯虚函数
};
```

### 访问 Emulated Pose Manager

```cpp
#include "XRScribeEmulatedPoseManager.h"

// FOpenXRActionPoseManager 管理捕获的姿态数据和输入状态
// 它在 Emulation 层内部使用，提供：
// - 从捕获历史中生成插值姿态
// - 从捕获历史中回放动作状态（boolean, float, vector2f）
// - 支持 reference space 和 action space 的匹配与转换
```

## 架构概览

```
┌─────────────────────────────┐
│   UE Application (OpenXR)   │
├─────────────────────────────┤
│   XRScribe API Layer        │  ← 拦截所有 xr* 函数调用
│  ┌──────────┬──────────────┐│
│  │ Capture  │  Emulation   ││
│  │ Layer    │  Layer       ││
│  │          │              ││
│  │ Encoder  │  Decoder     ││
│  │          │  PoseManager ││
│  └──────────┴──────────────┘│
├─────────────────────────────┤
│   OpenXR Runtime (真实)      │
└─────────────────────────────┘
```

### 文件格式 (.xrs)

Capture 文件使用 UE 的 `FArchive` 序列化机制。每个 OpenXR API 调用被编码为一个 `FOpenXRAPIPacketBase` 包结构，包含：
- 时间戳 (`TimeInCycles`)
- API 返回值 (`XrResult`)
- API ID (`EOpenXRAPIPacketId`)
- 线程 ID (`EOpenXRAPIThreadId`: GameThread / RenderThread / RHIThread)
- 对应 API 的参数数据

默认保存路径：`Saved/Capture.xrs`

### 支持的 OpenXR 扩展

XRScribe 支持拦截以下扩展（通过编译宏控制）：
- `XR_KHR_D3D11_enable` — D3D11 图形绑定
- `XR_KHR_D3D12_enable` — D3D12 图形绑定
- `XR_KHR_opengl_enable` — OpenGL 图形绑定
- `XR_KHR_vulkan_enable` — Vulkan 图形绑定
- `XR_KHR_visibility_mask` — 可见性遮罩
- `XR_KHR_loader_init` — 加载器初始化

## Demo 示例

XRScribe 不需要编写代码即可使用。以下是最小配置步骤：

### Step 1: 启用 Plugin

在 `.uproject` 文件中添加：

```json
{
    "Plugins": [
        {
            "Name": "XRScribe",
            "Enabled": true
        }
    ]
}
```

### Step 2: Capture 模式（在有头显的机器上）

`DefaultEngine.ini`:
```ini
[XRScribe]
RunMode=0
```

启动引擎，连接头显，正常进行 VR 交互。结束后会在 `Saved/Capture.xrs` 生成录制文件。

### Step 3: Emulate 模式（在没有头显的机器上）

将 `Capture.xrs` 复制到目标机器的 `Saved/` 目录，然后：

`DefaultEngine.ini`:
```ini
[XRScribe]
RunMode=1
```

启动引擎，XRScribe 会从文件加载并回放 OpenXR 会话。

## 模块依赖

从 `XRScribe.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `OpenXR` | OpenXR 功能库 |
| `OpenXRHMD` | OpenXR HMD 集成 |
| `RHI` | 渲染硬件接口（用于图形绑定） |

Private 依赖：

| 模块 | 用途 |
|---|---|
| `DeveloperSettings` | 开发者设置系统（`UXRScribeDeveloperSettings`） |
| `Projects` | 项目信息访问 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2026-04-13 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 代码风格统一，将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-04-13 | `ab338b00` | Migrate UE_LOG to UE_LOGF | 同上，分两次提交完成 |
| 2025-10-30 | `09e49c84` | Replace use of RHIGetNativeDevice with RHIGetDevice functions | RHI 接口重构，提升类型安全性 |

### 维护评价

- **创建时间**: 2023-04-25，约 3 年历史
- **更新频率**: 最近一次实质性更新在 2025-10-30（RHI 重构），2026-04 的更新仅为日志宏迁移（非功能性）
- **实验性标记**: `.uplugin` 中 `IsExperimentalVersion = true`，`EnabledByDefault = false`
- **平台限制**: 仅 Win64
- **综合评价**: 实验性 plugin，仍处于开发早期阶段。API Surface 中有大量 TODO 注释（如运行时切换模式、自定义录制路径、其他运行模式等），说明功能尚未完全稳定。适合对 XR 开发工具链有需求的高级用户，不建议在生产环境依赖。如果 2025-10 的 RHI 重构是最后一次实质性功能变更，距今已超过 6 个月，维护节奏偏慢。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/XR/XRScribe)
- [官方文档]()（无，`.uplugin` 的 DocsURL 为空）
- [OpenXR 规范](https://www.khronos.org/openxr/)
