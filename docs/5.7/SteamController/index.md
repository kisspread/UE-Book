# Steam Controller Plugin

> InputDevice plugin for Steam controller

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | SteamController (Runtime) |
| 创建时间 | 2015-01-23 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamController) | |

## 用途

这是一个基于 Steam Input API 的输入设备插件，将 Steam Controller（以及其他支持 Steam Input 的控制器）接入 UE5 的输入系统。它通过 Steamworks SDK 的 `ISteamInput` 接口读取数字动作（按钮）和模拟动作（摇杆/触控板），并将它们映射为 UE 的标准 Gamepad 按键事件，使得项目无需额外代码即可在 Steam Input 设备上使用 UE 原生的 Action/Axis 映射系统。

简而言之：它让 UE 的 Input Settings 里的 Action/Axis 映射自动生效于 Steam 控制器。

## 使用场景

- 你的游戏通过 Steam 发布，并且需要支持 Steam Controller 或 Steam Input 兼容的手柄
- 你想利用 Steam Input 的动作（Action）映射系统，让玩家在 Steam 客户端中自定义按键布局
- 你需要在 UE 中同时处理传统手柄和 Steam 控制器输入，而不想写两套代码

**注意**：此插件默认未启用（`EnabledByDefault: false`），需要在项目设置或 `.uproject` 中手动启用。

## 蓝图用法

本插件没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是一个纯运行时输入设备模块，功能完全在底层自动运行：

- 启用插件后，Steam 控制器的输入会自动映射到你在 **Project Settings → Input** 中定义的 Action/Axis 映射
- 你可以在蓝图中像处理普通手柄一样处理 Steam 控制器的按键事件
- Force Feedback（力反馈）也会自动通过 Steam 的触觉脉冲（Haptic Pulse）实现

### 使用方式（蓝图描述）

1. 在 Project Settings → Input 中定义你的 Action/Axis 映射
2. 在蓝图中使用 `InputAction` 或 `InputAxis` 节点监听输入
3. Steam 控制器的按键会自动触发这些节点，无需特殊处理

## C++ 用法

### 头文件引入

```cpp
#include "ISteamControllerPlugin.h"
```

### 模块可用性检查

```cpp
// 检查 SteamController 模块是否已加载
if (ISteamControllerPlugin::IsAvailable())
{
    // 获取模块单例
    ISteamControllerPlugin& SteamControllerModule = ISteamControllerPlugin::Get();
}
```

### 工作原理

插件在初始化时自动完成以下工作：

1. **初始化 Steam Input API**：调用 `SteamInput()->Init()` 初始化
2. **读取 Input Settings**：遍历项目中定义的所有 Action 和 Axis 映射
3. **映射 Steam Action**：将 UE 的 Action 名称通过 `SteamInput()->GetDigitalActionHandle()` 和 `GetAnalogActionHandle()` 转换为 Steam Action Handle
4. **每帧轮询**：在 `SendControllerEvents()` 中读取所有已连接控制器的输入状态，转换为 UE 标准按键事件
5. **支持力反馈**：通过 `Legacy_TriggerHapticPulse()` 实现触觉反馈

### 关键限制

- **平台限制**：仅支持 Win64 和 Linux（排除 Win64:arm64）
- **需要 Steam 运行时**：必须在 Steam 客户端环境下运行
- **最多 8 个控制器**：硬编码 `MAX_STEAM_CONTROLLERS = 8`
- **Action 名称匹配**：Steam Action 名称必须与 UE Input Settings 中的 Action/Axis 名称完全一致
- **已知问题**：源码注释中标注了 `// [RCL] 2015-01-23 FIXME: move to some other code than constructor`，初始化失败处理不够优雅

## Demo 示例

### 最小配置示例

**1. 启用插件**

在 `.uproject` 中添加：

```json
{
    "Plugins": [
        {
            "Name": "SteamController",
            "Enabled": true
        }
    ]
}
```

**2. Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "SteamController"
});
```

**3. C++ 中检查模块状态**

```cpp
// MyGameMode.cpp
#include "ISteamControllerPlugin.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (ISteamControllerPlugin::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("Steam Controller plugin is active"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Steam Controller plugin is not available"));
    }
}
```

## 模块依赖

从 `SteamController.Build.cs` 的依赖声明提取：

| 模块 | 类型 | 用途 |
|---|---|---|
| `InputDevice` | Public | 输入设备基础框架 |
| `InputCore` | Public | 核心输入类型定义（FKey 等） |
| `Core` | Private | UE 核心库 |
| `CoreUObject` | Private | UObject 系统 |
| `ApplicationCore` | Private | 平台抽象层 |
| `Engine` | Private | 引擎核心（InputSettings 等） |
| `SteamShared` | Private / Plugin | Steam 共享模块，管理 Steam API 初始化 |
| `Steamworks` | ThirdParty | Valve Steamworks SDK |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-06-03 | `0a44e4b8` | 支持按 CPU 架构排除/包含插件模块（新增 `PlatformArchitectureDenyList`，排除 arm64） |
| 2025-05-22 | `97f9ce7f` | 修复 SteamController 插件关闭时的竞争条件崩溃（UE-281929） |
| 2023-03-06 | `0ac2dd67` | 硬件设备标识符新增 `EHardwareDeviceSupportedFeatures` 和 `EHardwareDevicePrimaryType` 枚举 |

### 维护评价

- **创建时间**：2015 年 1 月，已超过 11 年历史（🏛️ 文物级插件）
- **更新频率**：2023 年有一次功能性更新，2025 年有两次（一次 bug 修复，一次架构级改动）
- **维护状态**：**维护中** — 虽然代码量极小且变化不大，但近 2 年仍有实质性修复（包括一个崩溃修复），说明 Epic 仍在关注此模块
- **已知限制**：
  - 使用已废弃的 `Legacy_TriggerHapticPulse` API，未来 Steamworks SDK 可能移除此接口
  - 初始化逻辑在构造函数中，错误处理不够健壮
  - 功能非常基础，不支持 Steam Input 的高级特性（如动作集切换、陀螺仪等）
- **推荐程度**：如果你的游戏通过 Steam 发布且需要 Steam Controller 支持，这是一个开箱即用的基础方案。但如果你需要更完整的 Steam Input 功能，可能需要自行扩展或使用第三方方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamController)
- [Steamworks Input 文档](https://partner.steamgames.com/doc/features/steamcontroller)
