# Virtual Production Settings

> Allows users to manage Virtual Production settings.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片设置 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VPSettings` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPSettings) | |

## 用途

提供虚拟制片（Virtual Production）中的通用配置数据，包括虚拟摄像机的常用参数预设（焦距、光圈、快门速度、ISO）以及制作人员/项目标识信息。该插件通过 `UVPSettings` 全局单例对象，让蓝图或 C++ 代码在运行时读取或修改这些配置，无需直接编辑配置文件。

> **注意**：`UVPSettings` 中的角色（Roles）相关功能已弃用，请改用 `UVirtualProductionRolesSubsystem`。

## 使用场景

- 在虚拟制片项目中统一摄像机参数预设，例如快速切换标准电影级焦距列表。
- 记录当前导演名称与项目名称，用于元数据输出或 UI 显示。
- 在编辑器中控制角色标签是否可见（实验性功能）。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get VPSettings` | 获取全局唯一的 `UVPSettings` 实例 | `UVPSettings` |

### 可读写的属性（BlueprintReadWrite）

| 属性名 | 类型 | 说明 |
|---|---|---|
| `FocalLengthPresets` | `TArray<float>` | 虚拟摄像机焦距预设列表（默认：18, 21, 25, 32, 40, 50, 65, 75, 100, 135） |
| `AperturePresets` | `TArray<float>` | 虚拟摄像机光圈预设列表（默认：1.0, 1.4, ... 22.0） |
| `DefaultShutterSpeedPresets` | `TArray<float>` | 虚拟摄像机快门速度预设列表（1/s，默认：1, 4, 8, ... 1000） |
| `DefaultISOPresets` | `TArray<float>` | 虚拟摄像机 ISO 预设列表（默认：50, 100, ... 6400） |
| `DirectorName` | `FString` | 导演名称（默认 "Default Director"） |
| `ShowName` | `FString` | 项目/节目名称（默认 "Default Project"） |
| `bShowRoleInEditor` | `bool` | （编辑器专用）是否在主编辑器 UI 中显示虚拟制片角色 |

### 使用示例（蓝图描述）

1. 获取 `UVPSettings` 对象：`Get VPSettings → Return Value`。
2. 从返回的对象中直接读取任意属性，例如将 `FocalLengthPresets` 连接到下拉菜单的选项源。
3. 在关卡蓝图或游戏模式中修改 `DirectorName`，用于存档或 UI 显示。

## C++ 用法

### 头文件引入

```cpp
#include "VPSettings.h"
```

### 基本用法

```cpp
// 获取单例
UVPSettings* VPSettings = UVPSettings::GetVPSettings();

// 读取预设列表
TArray<float> Focals = VPSettings->FocalLengthPresets;

// 修改项目名称
VPSettings->ShowName = TEXT("MyVirtualProduction");
VPSettings->SaveConfig();  // 保存到默认配置文件中
```

### 进阶用法

在初始化阶段自定义预设值（例如从外部文件导入）：

```cpp
void AMyGameMode::InitDefaultCamPresets()
{
    UVPSettings* Settings = UVPSettings::GetVPSettings();
    Settings->AperturePresets = { 1.4, 2.0, 2.8, 4.0, 5.6 };
    Settings->DefaultShutterSpeedPresets = { 30.0, 60.0, 125.0, 250.0 };
    Settings->DefaultISOPresets = { 100, 200, 400, 800 };
    Settings->SaveConfig();
}
```

## Demo 示例

以下是一个最小示例，展示如何在游戏模式下获取并打印虚拟摄像机预设。

### VPSettingsDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "VPSettingsDemo.generated.h"

UCLASS()
class AVPSettingsDemoGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "VP Demo")
    void LogCameraPresets();
};
```

### VPSettingsDemo.cpp

```cpp
#include "VPSettingsDemo.h"
#include "VPSettings.h"
#include "Engine/Engine.h"

void AVPSettingsDemoGameMode::BeginPlay()
{
    Super::BeginPlay();
    LogCameraPresets();
}

void AVPSettingsDemoGameMode::LogCameraPresets()
{
    UVPSettings* VPSettings = UVPSettings::GetVPSettings();
    if (VPSettings)
    {
        FString FocalStr = FString::JoinBy(VPSettings->FocalLengthPresets, TEXT(", "), [](float V) { return FString::SanitizeFloat(V); });
        UE_LOG(LogTemp, Log, TEXT("Focal Length Presets: %s"), *FocalStr);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 提供 `FGameplayTagContainer` 支持（用于角色标识，虽已弃用但仍保留） |

其余依赖均为标准 Core/Engine 模块，在此不列。

## 维护状态

### 近期更新

- 2025-08-19 `c17d797b` — VP Roles - Update deprecation comment
- 2023-05-03 `c0d8c5ac` — VPSettings: Moved DirectorName and ShowName from WITH_EDITORONLY_DATA block to PUBLIC.
- 2023-01-12 `be1992fa` — Move VPSettings and VPRoles into their own modules / plugins.

### 维护评价

该插件于 2023 年创建，目前处于实验阶段（Beta）。除 2025 年的一次注释更新外，自 2023 年 5 月以来未收到功能性更新。核心功能（角色管理）已被标记为弃用并推荐使用 `UVirtualProductionRolesSubsystem`。当前插件仅保留预设值和项目名称配置功能，维护不活跃。在 UE5 新项目中建议优先使用官方的虚拟制片子系统或自行实现配置管理，而不是依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProduction/VPSettings)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/VirtualProduction/VPSettings/Source/VPSettings.Build.cs)（Build.cs 仅为模块定义，无独立测试文件）