# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇外设灯效 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产类型定义） |
| 模块 | `RazerChromaDevices` (ClientOnlyNoCommandlet), `RazerChromaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices) | |

## 用途

这个插件让 UE5 游戏能够在运行时控制雷蛇（Razer）外设的 Chroma RGB 灯效。核心流程是：从 Razer Chroma 官网下载或制作 `.chroma` 动画文件 → 作为资产导入引擎 → 在游戏运行时通过蓝图或 C++ 播放这些动画，让玩家的键盘、鼠标、耳机等雷蛇外设同步显示灯光效果。

插件通过动态加载 Razer Chroma SDK 的 DLL 来实现所有功能，如果玩家机器上没有安装 Razer Synapse（雷蛇驱动软件），则灯效功能不可用，但不会影响游戏本身的运行。

## 使用场景

- 你在做一款支持雷蛇外设灯效的游戏 → 导入 `.chroma` 动画文件，在游戏事件（如受击、拾取道具）时播放灯光动画
- 你想让键盘根据游戏状态变色 → 使用 `SetAllDevicesStaticColor` 设置静态颜色
- 你想在没有其他灯效播放时显示一个待机动画 → 通过项目设置配置 IdleAnimation
- 你希望通过 Unreal 的 Input Device Property 系统控制灯效 → 启用 `bCreateRazerChromaInputDevice` 后使用 `URazerChromaPlayAnimationFile` 属性

## 蓝图用法

所有游戏逻辑相关的功能都在 `URazerChromaFunctionLibrary` 中暴露为蓝图节点，均为静态函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsChromaRuntimeAvailable` | 检查 Razer Chroma 运行时是否可用 | `URazerChromaFunctionLibrary` |
| `PlayChromaAnimation` | 播放指定的 Chroma 动画（可选循环） | `URazerChromaFunctionLibrary` |
| `StopChromaAnimation` | 停止指定动画 | `URazerChromaFunctionLibrary` |
| `PauseChromaAnimation` | 暂停指定动画 | `URazerChromaFunctionLibrary` |
| `ResumeChromaAnimation` | 恢复已暂停的动画 | `URazerChromaFunctionLibrary` |
| `IsAnimationPlaying` | 查询动画是否正在播放 | `URazerChromaFunctionLibrary` |
| `IsChromaAnimationPaused` | 查询动画是否已暂停 | `URazerChromaFunctionLibrary` |
| `StopAllChromaAnimations` | 停止所有正在播放的动画 | `URazerChromaFunctionLibrary` |
| `SetAllDevicesStaticColor` | 将所有指定类型设备设为静态颜色 | `URazerChromaFunctionLibrary` |
| `SetIdleAnimation` | 设置待机动画（无其他动画播放时显示） | `URazerChromaFunctionLibrary` |
| `SetUseIdleAnimation` | 开启/关闭待机动画功能 | `URazerChromaFunctionLibrary` |
| `GetTotalDuration` | 获取动画时长（秒） | `URazerChromaFunctionLibrary` |
| `SetEventName` | 命名 Chroma 事件（可附加触觉反馈等） | `URazerChromaFunctionLibrary` |
| `UseForwardChromaEvents` | 是否在播放动画时自动转发事件名 | `URazerChromaFunctionLibrary` |

### 设备类型枚举 `ERazerChromaDeviceTypes`

这是一个位掩码枚举，用于 `SetAllDevicesStaticColor` 时指定目标设备：

| 值 | 设备类型 |
|---|---|
| `Keyboards` | 键盘 |
| `Mice` | 鼠标 |
| `Headset` | 耳机 |
| `Mousepads` | 鼠标垫 |
| `Keypads` | 键区 |
| `ChromaLink` | ChromaLink 设备 |
| `All` | 以上所有 |

### 使用示例（蓝图描述）

**播放灯光动画：**
1. 先调用 `IsChromaRuntimeAvailable` 检查运行时是否可用
2. 资产引用你的 `RazerChromaAnimationAsset`（在 Content Browser 中创建）
3. 连接到 `PlayChromaAnimation` 的 `AnimToPlay` 引脚，`bLooping` 设为 true/false
4. 返回值为 bool，表示是否成功播放

**设置静态颜色：**
1. 调用 `SetAllDevicesStaticColor`，传入 FColor（如红色 `(255,0,0,255)`）
2. `DeviceTypes` 参数为位掩码，设为 `0` 表示 All，或按需组合

**动画生命周期管理：**
- 播放 → `PlayChromaAnimation`
- 查询状态 → `IsAnimationPlaying` / `IsChromaAnimationPaused`
- 暂停 → `PauseChromaAnimation`
- 恢复 → `ResumeChromaAnimation`（可选是否循环）
- 停止 → `StopChromaAnimation`
- 停止全部 → `StopAllChromaAnimations`

## C++ 用法

### 头文件引入

```cpp
#include "RazerChromaFunctionLibrary.h"
#include "RazerChromaAnimationAsset.h"
#include "RazerChromaDevicesDeveloperSettings.h"
```

### 基本用法

来自 `Public/RazerChromaFunctionLibrary.h` 的公共 API：

```cpp
// 检查 Razer Chroma 运行时是否可用
if (URazerChromaFunctionLibrary::IsChromaRuntimeAvailable())
{
    // 播放一个 Chroma 动画（需要持有 URazerChromaAnimationAsset 引用）
    URazerChromaAnimationAsset* MyAnim = /* 从资产加载或引用 */;
    bool bSuccess = URazerChromaFunctionLibrary::PlayChromaAnimation(MyAnim, /*bLooping=*/false);

    // 查询播放状态
    bool bPlaying = URazerChromaFunctionLibrary::IsAnimationPlaying(MyAnim);
    float Duration = URazerChromaFunctionLibrary::GetTotalDuration(MyAnim);

    // 暂停 / 恢复 / 停止
    URazerChromaFunctionLibrary::PauseChromaAnimation(MyAnim);
    bool bPaused = URazerChromaFunctionLibrary::IsChromaAnimationPaused(MyAnim);
    URazerChromaFunctionLibrary::ResumeChromaAnimation(MyAnim, /*bLoop=*/true);
    URazerChromaFunctionLibrary::StopChromaAnimation(MyAnim);
}
```

### 进阶用法

**设置静态颜色（指定设备类型）：**

```cpp
#include "RazerChromaDevicesDeveloperSettings.h"  // ERazerChromaDeviceTypes 枚举定义

// 将键盘和鼠标设为蓝色
FColor BlueColor(0, 0, 255, 255);
int32 DeviceMask = static_cast<int32>(ERazerChromaDeviceTypes::Keyboards) 
                 | static_cast<int32>(ERazerChromaDeviceTypes::Mice);
URazerChromaFunctionLibrary::SetAllDevicesStaticColor(BlueColor, DeviceMask);

// 设置所有设备为红色（蓝图版本使用 int32 位掩码）
URazerChromaFunctionLibrary::SetAllDevicesStaticColor(FColor::Red, static_cast<int32>(ERazerChromaDeviceTypes::All));
```

**C++ 重载版本（直接使用 FColor + 枚举）：**

```cpp
// 库提供了直接接受 ERazerChromaDeviceTypes 枚举的 C++ 重载
URazerChromaFunctionLibrary::SetAllDevicesStaticColor(FColor::Green, ERazerChromaDeviceTypes::All);
```

**配置待机动画：**

```cpp
URazerChromaAnimationAsset* IdleAnim = /* 加载或引用 */;
URazerChromaFunctionLibrary::SetIdleAnimation(IdleAnim);
URazerChromaFunctionLibrary::SetUseIdleAnimation(true);
```

**事件系统集成：**

```cpp
// 为 Chroma 事件命名（支持触觉反馈等附加功能）
URazerChromaFunctionLibrary::SetEventName(TEXT("Explosion_Event"));

// 配置是否在播放动画时自动转发事件名
URazerChromaFunctionLibrary::UseForwardChromaEvents(true);
```

## Demo 示例

### 使用 Input Device Property 播放动画

`URazerChromaPlayAnimationFile` 是一个 `UInputDeviceProperty` 子类，可通过 Unreal 的 Input Device Property 系统使用：

```cpp
// MyChromaProperty.h
#pragma once

#include "CoreMinimal.h"
#include "RazerChromaDeviceProperties.h"

// 通过 CreateDefaultSubobject 或在蓝图中创建 URazerChromaPlayAnimationFile 实例
// 然后通过 Input Device Subsystem 设置属性即可播放动画
```

```cpp
// 示例：通过 InputDeviceSubsystem 设置属性
// URazerChromaPlayAnimationFile* ChromaProp = NewObject<URazerChromaPlayAnimationFile>();
// ChromaProp->AnimAsset = MyAnimationAsset;
// ChromaProp->bLooping = true;
// // 然后通过 GetInputDeviceSubsystem() 设置到对应的控制器上
```

### 开发者设置配置

在项目设置 → Razer Chroma Settings 中配置：

```
项目设置
├── Razer Chroma
│   ├── bIsRazerChromaEnabled = true          // 总开关
│   ├── bCreateRazerChromaInputDevice = false  // 是否创建输入设备
│   ├── IdleAnimationAsset = (指定资产)        // 待机动画
│   ├── bUseChromaAppInfoForInit = true        // 使用 App 信息初始化
│   └── App Configuration
│       ├── ApplicationTitle = "My Game"
│       ├── ApplicationDescription = "A cool game"
│       ├── AuthorName = "My Studio"
│       ├── AuthorContact = "support@mystudio.com"
│       └── SupportedDeviceTypes = (位掩码选择)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RazerChromaSDK` | Razer Chroma SDK 的外部封装模块（插件自身提供，用于动态加载 RazerChroma.dll） |

无其他特殊依赖（仅标准 Core/Engine/InputCore 等）。

> **注意**：该插件默认禁用（`EnabledByDefault: false`），需要在项目设置的 Plugins 中手动启用。启用后需要重启编辑器才能生效。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器的函数类型转换警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2025-09-30 | `96cf6b99` | Removed 32-bit support. | 移除 32 位平台支持 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 优化编译 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 优化编译 |

### 维护评价

- **创建时间**：2024 年 3 月，相对较新的插件
- **状态**：仍标记为 `IsBetaVersion=true`，实验性质
- **更新频率**：近期更新均为引擎级维护性修改（编译器兼容性、日志宏迁移、32 位移除），**无功能性更新**
- **已知限制**：
  - 需要玩家机器上安装 Razer Synapse 才能工作
  - 仅支持 Windows 平台（ClientOnlyNoCommandlet）
  - 仍处于 Beta 阶段，API 可能发生变化
  - `ApplicationName` 的 TODO 注释表明动画名唯一性校验尚未实现
- **推荐**：可以用于实验和原型开发，但用于生产环境需谨慎，因为 API 仍可能变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices)
- [Razer Chroma 官网](https://www.razer.com/chroma)（用于制作 .chroma 动画文件）