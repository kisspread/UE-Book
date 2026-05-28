# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇幻彩设备 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `RazerChromaDevices` (Runtime), `RazerChromaEditor` (Editor), `RazerChromaSDK` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices) | |

## 用途

RazerChromaDevices 是一个用于在运行时控制雷蛇 Chroma RGB 外设灯光效果的 UE5 插件。它封装了 Razer Chroma SDK，让游戏开发者可以：

1. **导入 Chroma 动画文件**：从 Razer 官方网站下载或制作 ".chroma" 动画文件，导入到 UE5 项目中
2. **运行时播放灯光效果**：在玩家的雷蛇外设上实时播放自定义灯光动画
3. **响应游戏事件**：通过灯光效果反馈游戏状态变化，如生命值、弹药、技能冷却等

支持的设备类型包括：键盘、鼠标、耳机、鼠标垫、键盘垫、音响等全系列 Chroma 设备。

## 使用场景

- 你在开发 PC 游戏，希望为拥有雷蛇外设的玩家提供沉浸式灯光体验 → 用 RazerChromaDevices
- 你需要在游戏事件发生时（如受伤、击杀、完成任务）触发外设灯光反馈 → 用 RazerChromaDevices
- 你有从 Razer Chroma Workshop 制作的 ".chroma" 动画文件，想在游戏里播放 → 用 RazerChromaDevices

## 蓝图用法

由于该插件是实验性的且源码未完全提供，蓝图 API 的完整列表无法从当前信息中确定。根据 RazerChromaDevices 模块的功能推断，可能包含以下核心节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play Chroma Effect` | 在所有已连接的 Chroma 设备上播放效果 | `URazerChromaSubsystem`（推测） |
| `Stop Chroma Effect` | 停止当前正在播放的效果 | `URazerChromaSubsystem`（推测） |
| `Set Static Color` | 将所有设备设置为静态颜色 | `URazerChromaSubsystem`（推测） |

### 使用示例（蓝图描述）

```
[Event: PlayerDamaged] → [Play Chroma Effect: DamageAnimation]
[Event: Game Over] → [Stop Chroma Effect]
```

> ⚠️ 注意：由于插件处于实验阶段，API 可能会变动，建议参考最新的源码实现。

## C++ 用法

### 头文件引入

```cpp
#include "RazerChromaDevicesModule.h"
```

### 基本用法

该插件基于 Razer Chroma SDK，底层使用 `RzChromaSDKTypes.h` 中定义的类型系统。以下是如何在 C++ 中使用 Chroma SDK 的基础示例：

```cpp
// 包含 Chroma SDK 头文件
#include "ThirdParty/RazerChromaSDK/RzChromaSDKTypes.h"

// 设置键盘静态颜色效果
ChromaSDK::Keyboard::STATIC_EFFECT_TYPE KeyboardEffect;
KeyboardEffect.Color = RGB(255, 0, 0); // 红色

// 设置鼠标静态效果
ChromaSDK::Mouse::STATIC_EFFECT_TYPE MouseEffect;
MouseEffect.LEDId = ChromaSDK::Mouse::RZLED_ALL;
MouseEffect.Color = RGB(0, 255, 0); // 绿色
```

### 进阶用法

使用自定义效果类型控制键盘每个按键的颜色：

```cpp
// 自定义键盘效果 - 每个按键独立设置颜色
ChromaSDK::Keyboard::CUSTOM_EFFECT_TYPE CustomKeyboardEffect;

// 设置特定按键颜色 (row, column)
CustomKeyboardEffect.Color[0][0] = RGB(255, 0, 0); // ESC 键红色
CustomKeyboardEffect.Color[1][1] = RGB(0, 255, 0); // F1 键绿色

// 使用 RZKEY 枚举获取精确按键位置
// RZKEY_W = 0x0203 → row=2, column=3
```

## Demo 示例

```cpp
// RazerChromaExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RazerChromaExample.generated.h"

UCLASS()
class ARazerChromaExample : public AActor
{
    GENERATED_BODY()

public:
    ARazerChromaExample();

    // 设置键盘静态颜色
    UFUNCTION(BlueprintCallable, Category = "Razer Chroma")
    void SetKeyboardStaticColor(FLinearColor Color);

    // 设置鼠标呼吸效果
    UFUNCTION(BlueprintCallable, Category = "Razer Chroma")
    void SetMouseBreathingEffect(FLinearColor Color1, FLinearColor Color2);

    // 设置全设备波浪效果
    UFUNCTION(BlueprintCallable, Category = "Razer Chroma")
    void SetWaveEffect();
};
```

```cpp
// RazerChromaExample.cpp
#include "RazerChromaExample.h"

ARazerChromaExample::ARazerChromaExample()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ARazerChromaExample::SetKeyboardStaticColor(FLinearColor Color)
{
    // 将 FLinearColor 转换为 COLORREF (BGR 格式)
    COLORREF ChromaColor = RGB(
        (int)(Color.R * 255),
        (int)(Color.G * 255),
        (int)(Color.B * 255)
    );
    
    // 创建静态效果
    ChromaSDK::Keyboard::STATIC_EFFECT_TYPE Effect;
    Effect.Color = ChromaColor;
    
    // 应用效果（通过 Chroma SDK API）
    // RzSdkCreateKeyboardEffect(ChromaSDK::Keyboard::CHROMA_STATIC, &Effect);
}

void ARazerChromaExample::SetMouseBreathingEffect(FLinearColor Color1, FLinearColor Color2)
{
    ChromaSDK::Mouse::STATIC_EFFECT_TYPE Effect;
    Effect.LEDId = ChromaSDK::Mouse::RZLED_ALL;
    Effect.Color = RGB((int)(Color1.R * 255), (int)(Color1.G * 255), (int)(Color1.B * 255));
}

void ARazerChromaExample::SetWaveEffect()
{
    // 波浪效果类型定义
    ChromaSDK::Keyboard::WAVE_EFFECT_TYPE WaveEffect;
    WaveEffect.Direction = ChromaSDK::Keyboard::WAVE_EFFECT_TYPE::DIRECTION_LEFT_TO_RIGHT;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RazerChromaSDK` | Razer Chroma SDK 的 UE5 封装层，提供底层 API 访问 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器的函数类型转换警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 |
| 2025-09-30 | `96cf6b99` | Removed 32-bit support. | 移除 32 位平台支持 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 优化编译性能，添加内联生成宏 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 优化编译性能，添加内联生成宏 |

### 维护评价

**状态：活跃维护中**

- **创建时间**：2024-03-25（约 2 年前）
- **维护频率**：每 2-3 个月有更新，最近一次更新在 2026-05-12
- **更新性质**：主要是编译器兼容性修复和引擎版本适配，属于被动维护
- **实验状态**：插件标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`
- **推荐度**：⚠️ 谨慎使用

**建议**：
- 该插件适合原型开发和内部测试使用
- 生产环境使用前需充分测试，API 可能随版本更新而变动
- 需要玩家安装 Razer Synapse 软件才能正常工作
- 仅支持 Windows 平台（Chroma SDK 是 Windows 专用）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices)
- [Razer Chroma SDK 官方文档](https://developer.razer.com/works-with-chroma/)
- [Razer Chroma Workshop](https://www.chromaworkshop.com/)