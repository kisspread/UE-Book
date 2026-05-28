# Razer Chroma Devices

> Provides some functionality to set Razer Chroma effects at runtime.

| 属性 | 值 |
|---|---|
| 中文名 | 雷蛇彩光 |
| 分类 | Peripherals |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `RazerChromaDevices` (ClientOnlyNoCommandlet), `RazerChromaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices) | |

## 用途

该插件封装了 Razer Chroma SDK，使开发者能够将 Unreal Engine 的游戏事件与 Razer 外设（键盘、鼠标、耳机等）的 RGB 灯光效果进行联动。其核心功能是允许开发者导入在 Razer Chroma 网站设计并导出的 `.chroma` 动画文件，并在游戏中根据特定的游戏逻辑（如角色生命值变化、技能释放、游戏提示）来播放这些灯光动画，从而增强玩家的沉浸感。

## 使用场景

-   你正在开发一款 PC 游戏，并希望当玩家角色受到伤害时，其 Razer 键盘和鼠标能发出红色闪烁效果。
-   你的游戏需要突出显示某个可用技能或交互提示，希望通过玩家外设的灯光变化（如特定区域亮起）来给予视觉反馈。
-   你希望通过灯光效果同步游戏内的事件，例如在过场动画、任务完成或触发彩蛋时，为玩家的整个外设灯阵播放一段精心设计的动画。
-   你的游戏支持外设灯光自定义，允许玩家选择或预览不同的灯光主题。

## 蓝图用法

该插件提供了在蓝图中控制 Razer Chroma 灯光的核心功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetKeyboardColor` | 设置指定键盘按键区域的颜色 | `URazerChromaSubsystem` |
| `SetMouseColor` | 设置鼠标指定区域的颜色 | `URazerChromaSubsystem` |
| `ApplyKeyboardColorPattern` | 将一个预定义的颜色图案应用到键盘上 | `URazerChromaSubsystem` |
| `PlayAnimation` | 播放一个已导入的 .chroma 动画文件 | `URazerChromaSubsystem` |
| `StopAllEffects` | 停止所有正在播放的灯光效果，并将外设恢复到默认状态 | `URazerChromaSubsystem` |

### 使用示例（蓝图描述）

1.  **基本颜色控制**：在角色受到伤害的事件中，获取 `RazerChromaSubsystem`，然后调用 `SetKeyboardColor`，将 `ChromaColor` 参数设为红色，并将 `Key` 参数设为 “KEYBOARD_RZKEY_ALL”，使整个键盘瞬间变红。
2.  **播放动画**：首先通过内容浏览器导入一个 `.chroma` 资产。在游戏开始或某个特定事件触发时，调用 `PlayAnimation` 节点，并将导入的动画资产作为参数传入。可以通过返回值管理动画的生命周期。

## C++ 用法

### 头文件引入

```cpp
#include "RazerChromaSubsystem.h"
// 如果需要操作特定设备类型，可能还需包含
#include "ChromaTypes.h"
```

### 基本用法

通过游戏实例子系统获取插件接口，并设置简单的颜色。

```cpp
// 在某个 Actor 或 PlayerController 中
void AMyPlayerController::SetKeyboardToRed()
{
    // 获取游戏实例子系统
    URazerChromaSubsystem* ChromaSubsystem = GetGameInstance()->GetSubsystem<URazerChromaSubsystem>();
    if (ChromaSubsystem && ChromaSubsystem->IsChromaAvailable())
    {
        // 定义颜色 (RGB)
        FLinearColor RedColor(1.0f, 0.0f, 0.0f);
        // 设置整个键盘为红色
        ChromaSubsystem->SetKeyboardColor(ERazerChromaKey::KEYBOARD_RZKEY_ALL, RedColor);
    }
}
```
*（代码基于插件典型 API 模式推断）*

### 进阶用法

播放动画并处理错误。

```cpp
// 假设有一个 .chroma 动画资产的引用
UPROPERTY(EditAnywhere, BlueprintReadWrite)
UChromaAnimationAsset* MyAnimation;

void AMyPlayerController::PlayCustomAnimation()
{
    URazerChromaSubsystem* ChromaSubsystem = GetGameInstance()->GetSubsystem<URazerChromaSubsystem>();
    if (ChromaSubsystem && ChromaSubsystem->IsChromaAvailable() && MyAnimation)
    {
        // 播放动画，可以设置循环
        ChromaSubsystem->PlayAnimation(MyAnimation, true);
    }
    else
    {
        UE_LOG(LogChroma, Warning, TEXT("Chroma SDK not available or animation asset is null."));
    }
}
```
*（代码基于插件典型 API 模式推断）*

## Demo 示例

一个最小化示例，展示如何初始化并设置键盘颜色。

**MyChromaActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyChromaActor.generated.h"

UCLASS()
class AMyChromaActor : public AActor
{
    GENERATED_BODY()
public:
    AMyChromaActor();
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void ChangeKeyboardColor(bool bToBlue);

private:
    UPROPERTY()
    class URazerChromaSubsystem* ChromaSubsystem;
};
```

**MyChromaActor.cpp**
```cpp
#include "MyChromaActor.h"
#include "RazerChromaSubsystem.h"
#include "Engine/GameInstance.h"

AMyChromaActor::AMyChromaActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyChromaActor::BeginPlay()
{
    Super::BeginPlay();
    if (UGameInstance* GI = GetGameInstance())
    {
        ChromaSubsystem = GI->GetSubsystem<URazerChromaSubsystem>();
        if (ChromaSubsystem)
        {
            UE_LOG(LogTemp, Log, TEXT("Razer Chroma Subsystem obtained. SDK Available: %s"),
                ChromaSubsystem->IsChromaAvailable() ? TEXT("true") : TEXT("false"));
        }
    }
}

void AMyChromaActor::ChangeKeyboardColor(bool bToBlue)
{
    if (ChromaSubsystem && ChromaSubsystem->IsChromaAvailable())
    {
        FLinearColor NewColor = bToBlue ? FLinearColor::Blue : FLinearColor::Red;
        ChromaSubsystem->SetKeyboardColor(ERazerChromaKey::KEYBOARD_RZKEY_ALL, NewColor);
    }
}
```

## 模块依赖

要使用此插件，你的项目模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `RazerChromaDevices` | 插件的核心运行时逻辑，提供灯光控制的子系统接口。 |
| `RazerChromaSDK` | 插件封装的 Razer Chroma 官方 SDK 的外部库依赖。 |

*注意：运行时功能仅限客户端（`ClientOnlyNoCommandlet`）。编辑器工具（`RazerChromaEditor`）仅在编辑器环境下加载。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复了 MSVC 和 Clang 编译器之间的类型转换警告兼容性问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧式 UE_LOG 迁移到新的 UE_LOGF。 |
| 2025-09-30 | `96cf6b99` | Removed 32-bit support. | 移除了对 32 位平台的支持。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 优化了生成的 C++ 代码的内联方式。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 同上，为更多源文件添加了内联宏优化。 |

### 维护评价

-   **创建时间**：插件于 2024 年 3 月创建，历史不足两年。
-   **维护状态**：最后一次实质性提交（`3e657fb3`）距今约 2 周，虽然主要是编译器兼容性修复而非新功能，但表明插件仍在维护周期内。
-   **实验性**：插件明确标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，属于实验性功能。
-   **推荐度**：由于处于实验阶段，API 和功能在未来版本中可能会发生变化。建议仅在能够接受 API 变动风险的项目或原型开发中使用。对于正式产品，需密切关注后续版本更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RazerChromaDevices)
-   官方文档（暂无）
-   测试用例（插件内暂未发现）