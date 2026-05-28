# Virtual Production Settings

> Allows users to manage Virtual Production settings.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作设置 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `VPSettings` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPSettings) | |

## 用途

VPSettings 是一个运行时设置容器，其核心目的是集中管理和存储虚拟制作（Virtual Production）工作流中的全局配置与预设值。它主要解决两个问题：
1.  **统一配置入口**：为虚拟制作工作流（特别是虚拟摄像机相关的功能）提供一个可序列化、可跨项目共享的配置中心。
2.  **角色信息管理**：提供一个基础框架来存储和获取当前机器在虚拟制作中所担任的角色（例如“导演”、“摄影”），尽管此功能已被标记为废弃。

简而言之，这个插件是虚拟制作管线中用于存储“工厂设置”和“项目元数据”的基础设施。

## 使用场景

-   你在进行 LED 虚拟摄影棚（VP Stage）拍摄，需要为现场的所有虚拟摄像机预定义一组标准的焦距、光圈、快门速度等参数。
-   你的团队需要在不同的虚拟制作项目间快速切换，并且每个项目都有不同的默认导演名称、项目名称和角色配置。
-   你正在开发自定义的虚拟制作工具链，并希望从一个中心点读取标准化的预设值。

## 蓝图用法

`UVPSettings` 类提供了一个全局访问点和一个预设数据的存储库。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get VP Settings` | 获取全局的 UVPSettings 单例对象。 | `UVPSettings` |
| `Focal Length Presets` | 读取/设置虚拟摄像机的默认焦距预设列表。 | `UVPSettings` |
| `Aperture Presets` | 读取/设置虚拟摄像机的默认光圈预设列表。 | `UVPSettings` |
| `Default Shutter Speed Presets` | 读取/设置虚拟摄像机的默认快门速度预设列表。 | `UVPSettings` |
| `Default ISO Presets` | 读取/设置虚拟摄像机的默认 ISO 预设列表。 | `UVPSettings` |
| `Director Name` | 读取/设置当前虚拟制作项目的默认导演名称。 | `UVPSettings` |
| `Show Name` | 读取/设置当前虚拟制作项目的默认项目名称。 | `UVPSettings` |

### 使用示例（蓝图描述）

1.  在任何蓝图图表中，使用 `Get VP Settings` 节点获取 `UVPSettings` 对象。
2.  将其输出连接到一个 `Get` 类节点（例如 `Get Focal Length Presets`），即可在该蓝图中使用焦距预设数组。
3.  也可以使用 `Set` 类节点（例如 `Set Director Name`）动态修改当前项目的导演名称，此更改会保存在配置中。
4.  在 `Event BeginPlay` 中获取 `UVPSettings` 并读取 `Show Name`，然后将其显示在 UI 上。

## C++ 用法

### 头文件引入

```cpp
#include "VPSettings.h"
```

### 基本用法

通过 `UVPSettings::GetVPSettings()` 静态函数获取实例，并访问其 `UPROPERTY` 存储的预设值。

```cpp
// 来源：任意运行时模块
#include "VPSettings.h"

void SetupVirtualCameraDefaults()
{
    // 1. 获取全局 VPSettings 实例
    UVPSettings* Settings = UVPSettings::GetVPSettings();
    if (Settings)
    {
        // 2. 使用预设值初始化自定义摄像机组件
        MyCameraComponent->SetFocalLength(Settings->FocalLengthPresets[0]); // 18mm
        MyCameraComponent->SetAperture(Settings->AperturePresets[5]);       // f/5.6

        // 3. 读取项目信息用于UI或日志
        UE_LOG(LogTemp, Log, TEXT("Project: %s, Director: %s"), *Settings->ShowName, *Settings->DirectorName);
    }
}
```

### 进阶用法

在编辑器工具中动态修改预设值，这些修改会保存到 `DefaultGame.ini` 或项目配置文件中。

```cpp
// 来源：Editor 模块
#include "VPSettings.h"

void AddCustomFocalLength(float NewFocalLength)
{
    UVPSettings* Settings = UVPSettings::GetVPSettings();
    if (Settings)
    {
        // 检查并避免重复
        if (!Settings->FocalLengthPresets.Contains(NewFocalLength))
        {
            Settings->FocalLengthPresets.Add(NewFocalLength);
            // 排序以保持列表整洁
            Settings->FocalLengthPresets.Sort();
            // 修改需要标记为已修改以便保存到配置
            Settings->TryUpdateDefaultConfigFile();
            UE_LOG(LogTemp, Log, TEXT("Added Focal Length: %fmm"), NewFocalLength);
        }
    }
}
```

## Demo 示例

一个简单的 Actor，在 BeginPlay 时读取并打印 VPSettings 中的项目信息。

```cpp
// MyVPInfoPrinter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVPInfoPrinter.generated.h"

UCLASS()
class AMyVPInfoPrinter : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};

// MyVPInfoPrinter.cpp
#include "MyVPInfoPrinter.h"
#include "VPSettings.h" // 关键头文件

void AMyVPInfoPrinter::BeginPlay()
{
    Super::BeginPlay();

    // 获取 VPSettings 单例
    if (UVPSettings* VPSettings = UVPSettings::GetVPSettings())
    {
        // 打印读取到的项目信息
        UE_LOG(LogTemp, Warning, TEXT("Virtual Production Project: '%s'"), *VPSettings->ShowName);
        UE_LOG(LogTemp, Warning, TEXT("Director: '%s'"), *VPSettings->DirectorName);

        // 打印可用的焦距预设数量
        UE_LOG(LogTemp, Log, TEXT("Available Focal Length Presets: %d"), VPSettings->FocalLengthPresets.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get UVPSettings instance."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于存储和管理虚拟制作角色 (`Roles`) 的标签容器 (`FGameplayTagContainer`)。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数导致的警告。 |
| 2025-08-19 | `c17d797b` | VP Roles - Update deprecation comment | 更新了角色功能 (`Roles`) 相关废弃注释的指引说明。 |
| 2023-05-03 | `c0d8c5ac` | VPSettings: Moved DirectorName and ShowName from WITH_EDITORONLY_DATA block to PUBLIC. | 将导演和项目名称从仅编辑器数据块移至公共区域，使其在打包后的游戏中也可用。 |

### 维护评价

**维护不活跃**。该插件自 2023 年 5 月进行了最后一次实质性功能更新（移动 `DirectorName`/`ShowName` 属性）后，后续的更新仅为编译警告修复和废弃注释更新，已超过 2 年没有新功能添加。其内部的“角色”(`Roles`) 功能已在 UE 5.1 中被 `UVirtualProductionRolesSubsystem` 取代并标记为废弃。

**使用建议**：虽然插件本身功能稳定且仍在被其他虚拟制作工具（如 VCAM）依赖，但作为**新项目**，不建议直接使用此插件的 `Roles` 功能。它最稳定且无废弃警告的部分是**存储虚拟摄像机预设值** (`FocalLengthPresets` 等) 和**项目元数据** (`DirectorName`, `ShowName`)。如果你需要管理这些预设，它是一个有效的、可序列化的配置容器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPSettings)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProduction/VPSettings/Tests) (如果存在)