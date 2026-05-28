# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（未知类型） |
| 模块 | `MetaHumanPlatform` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-01-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPlatform) | |

## 用途

`MetaHumanPlatform` 模块是 MetaHuman Animator 插件的一个基础支撑模块，**其主要功能是进行系统硬件兼容性检测**。它通过查询 GPU 信息（如 LUID 和显存大小），来判断当前运行环境是否满足 MetaHuman 功能（如高性能实时渲染、面部动画解算等）的最低硬件要求。

此模块的存在是为了解决 MetaHuman 技术对高性能硬件的依赖问题。在运行 MetaHuman 相关的核心功能前，插件可以调用此模块的接口来检查系统条件，从而向用户提示兼容性信息或做出相应处理，确保用户体验。

## 使用场景

- **应用启动或场景加载时**：你需要检查玩家的设备是否具备运行 MetaHuman 角色的能力，以避免在低端设备上运行导致性能问题或功能失败。
- **在编辑器或工具中**：当用户尝试使用 MetaHuman Animator 的核心功能（如面部追踪、动画解算）时，工具需要验证硬件条件是否满足。

## 蓝图用法

该模块暴露的蓝图接口主要集中在硬件信息的静态查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Supported` | 静态函数，检查当前平台是否满足 MetaHuman 的最低硬件规格要求。 | `FMetaHumanMinSpec` |
| `Get Min Spec` | 静态函数，获取 MetaHuman 的最低规格描述文本。 | `FMetaHumanMinSpec` |
| `Reset` | 静态函数，重置硬件检测的缓存状态。 | `FMetaHumanMinSpec` |
| `Get LUIDs` | 静态函数，获取引擎使用的物理设备 LUID 以及系统中所有物理设备的 LUID 列表。 | `FMetaHumanPhysicalDeviceProvider` |
| `Get VRAM In MB` | 静态函数，获取主 GPU 的显存大小（单位：MB）。 | `FMetaHumanPhysicalDeviceProvider` |

### 使用示例（蓝图描述）

1. 在你的 `GameMode` 或 `PlayerController` 的 `BeginPlay` 事件中。
2. 调用 `FMetaHumanMinSpec::Is Supported` 节点。
3. 通过一个 `Branch` 节点判断返回的布尔值。
4. 如果为 `False`，可以调用 `Get Min Spec` 节点获取要求文本，并使用 `Print String` 或 UI 显示给用户。
5. 如果需要更详细的硬件信息，可以调用 `Get LUIDs` 和 `Get VRAM In MB` 进行日志记录或高级诊断。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"
```

### 基本用法

简单检查系统是否支持，并获取显存信息。

```cpp
// 来源: 基于 Public/MetaHumanMinSpec.h 和 Public/MetaHumanPhysicalDeviceProvider.h 的 API 设计
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"

void CheckMetaHumanSupport()
{
    // 1. 检查最低规格
    if (FMetaHumanMinSpec::IsSupported())
    {
        UE_LOG(LogTemp, Log, TEXT("当前设备满足 MetaHuman 的最低硬件要求。"));
    }
    else
    {
        FText MinSpecText = FMetaHumanMinSpec::GetMinSpec();
        UE_LOG(LogTemp, Warning, TEXT("设备不满足要求。%s"), *MinSpecText.ToString());
    }

    // 2. 获取显存信息
    int32 VRAM_MB = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();
    UE_LOG(LogTemp, Log, TEXT("主 GPU 显存: %d MB"), VRAM_MB);
}
```

### 进阶用法

获取所有 GPU 设备标识，用于多显卡环境下的调试。

```cpp
// 来源: 基于 Public/MetaHumanPhysicalDeviceProvider.h 的 API 设计
void LogPhysicalDeviceLUIDs()
{
    FString EngineLUID;
    TArray<FString> AllLUIDs;
    if (FMetaHumanPhysicalDeviceProvider::GetLUIDs(EngineLUID, AllLUIDs))
    {
        UE_LOG(LogTemp, Log, TEXT("引擎使用的物理设备 LUID: %s"), *EngineLUID);
        for (const FString& LUID : AllLUIDs)
        {
            UE_LOG(LogTemp, Log, TEXT("系统物理设备 LUID: %s"), *LUID);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("无法获取物理设备 LUID 信息。"));
    }
}
```

## Demo 示例

以下是一个可编译的最小示例，演示如何在游戏模块中使用 `MetaHumanPlatform` 进行硬件检测。

**MyGameMode.h**
```cpp
// MyGameMode.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;

private:
    /** 执行 MetaHuman 平台兼容性检查 */
    void PerformMetaHumanPlatformCheck();
};
```

**MyGameMode.cpp**
```cpp
// MyGameMode.cpp
#include "MyGameMode.h"
#include "MetaHumanMinSpec.h"
#include "MetaHumanPhysicalDeviceProvider.h"
#include "Kismet/GameplayStatics.h"

void AMyGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);

    PerformMetaHumanPlatformCheck();
}

void AMyGameMode::PerformMetaHumanPlatformCheck()
{
    // 重置可能存在的缓存，确保检查结果准确
    FMetaHumanMinSpec::Reset();

    const bool bIsSupported = FMetaHumanMinSpec::IsSupported();
    const FText MinSpecText = FMetaHumanMinSpec::GetMinSpec();
    const int32 VRAM_MB = FMetaHumanPhysicalDeviceProvider::GetVRAMInMB();

    if (bIsSupported)
    {
        UE_LOG(LogTemp, Display, TEXT("MetaHuman 平台检查通过。显存: %dMB。"), VRAM_MB);
        // 这里可以继续加载包含 MetaHuman 的场景
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MetaHuman 平台检查失败！最低要求: %s"), *MinSpecText.ToString());
        // 可以在这里弹出警告或回退到非 MetaHuman 的演示场景
        // UGameplayStatics::OpenLevel(this, FName("MainMenu"));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体跟踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在进行身体跟踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

- **活跃维护**：最近提交集中在 2026 年 5 月，更新非常频繁。
- **内容相关**：近期提交主要围绕 MetaHuman Animator 的身体跟踪、渲染和序列器功能进行修复和增强，表明整个插件（包括此平台模块所服务的上层功能）处于积极开发中。
- **稳定性**：`MetaHumanPlatform` 模块本身相对稳定，近期提交未直接修改其核心硬件检测逻辑，更多是上层功能适配。
- **推荐使用**：✅ **强烈推荐**。作为 MetaHuman 工具链的官方基础组件，它由 Epic 直接维护，集成度高，可靠性有保障。任何需要在运行时验证 MetaHuman 兼容性的项目都应使用此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPlatform)