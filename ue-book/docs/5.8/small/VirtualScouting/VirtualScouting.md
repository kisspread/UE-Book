# Virtual Scouting

> Virtual Scouting lets filmmakers scout a digital environment in virtual reality.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟场景勘察 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `VirtualScouting` (Runtime), `VirtualScoutingEditor` (Runtime), `VirtualScoutingOpenXR` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting) | |

## 用途

Virtual Scouting 插件为电影导演和摄影指导提供了一套完整的工具，让他们能够戴上 VR 头显，直接进入虚拟的拍摄场景中进行“实地”勘察。它不仅仅是一个 VR 浏览器，而是集成了场景导航、构图检查、镜头模拟、对象操作和序列规划等功能，旨在将传统的、基于屏幕的 3D 预可视化（Pre-vis）流程，升级为沉浸式的、直觉化的虚拟勘察体验。这解决了虚拟制片前期规划中，决策者无法“身临其境”感受空间关系和镜头语言的核心痛点。

## 使用场景

-   你正在为电影或剧集制作虚拟场景，导演希望像在真实片场一样走动、感受空间尺度和镜头构图 → **使用 Virtual Scouting 进行沉浸式预可视化**。
-   你的摄影指导需要在虚拟环境中测试不同的镜头焦距、光圈和宽高比，以确定最终拍摄方案 → **使用其集成的视图查找器工具**。
-   你需要在 VR 中快速放置、移动或旋转虚拟道具和角色模型，以规划复杂的场景布局 → **使用其集成的抓取与放置工具**。
-   你的团队需要规划虚拟摄像机的运动路径和关键帧，创建简单的虚拟拍摄序列 → **使用其序列工具**。

## 蓝图用法

从 `VirtualScoutingSettings.h` 源码中提取的关键蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Virtual Scouting Settings` | 获取项目级的虚拟勘察设置单例 | `UVirtualScoutingSettings` |
| `Get Virtual Scouting Editor Settings` | 获取用户级的编辑器设置单例 | `UVirtualScoutingEditorSettings` |
| `Show Measurements in Imperial Units` | 读取/写入是否使用英制单位（英寸、英尺） | `UVirtualScoutingSettings` |
| `Viewfinder Use AutoExposure` | 读取/写入视图查找器是否启用自动曝光 | `UVirtualScoutingSettings` |
| `Swap to Grab on Spawn Actor` | 读取/写入生成新Actor后是否自动切换到抓取工具 | `UVirtualScoutingSettings` |
| `Viewfinder ExposureCompensation` | 读取/写入视图查找器的曝光补偿值 | `UVirtualScoutingSettings` |
| `Viewfinder Apertures` | 读取/写入可用的光圈值列表 | `UVirtualScoutingSettings` |
| `Viewfinder Monitor Masks` | 读取/写入可用的宽高比蒙版列表 | `UVirtualScoutingSettings` |
| `Flight Speed` | 读取/写入用户在VR中的飞行移动速度 | `UVirtualScoutingEditorSettings` |
| `Drag Speed` | 读取/写入用户在VR中拖拽移动的速度 | `UVirtualScoutingEditorSettings` |
| `Show Tooltips` | 读取/写入在VR中是否显示提示信息 | `UVirtualScoutingEditorSettings` |
| `Use Smooth Rotation` | 读取/写入是否使用平滑旋转（否则为快速旋转） | `UVirtualScoutingEditorSettings` |
| `Use Teleport Rotation` | 读取/写入是否使用传送时的旋转调整 | `UVirtualScoutingEditorSettings` |

### 使用示例（蓝图描述）

在你的任何蓝图（如关卡蓝图或专门的设置管理蓝图）中，首先通过“Get Virtual Scouting Settings”节点获取项目设置。然后，可以将其连接到各个属性的“Getter”节点（如 `Get Show Measurements in Imperial Units`）来读取当前配置，或者连接到“Setter”节点（如 `Set Viewfinder Apertures`）来动态修改配置。例如，你可以创建一个UI界面，让导演实时调整视图查找器的光圈值。

## C++ 用法

### 头文件引入

```cpp
#include "VirtualScoutingSettings.h"
```

### 基本用法

获取并访问项目的 Virtual Scouting 配置。
（来源：`Public/VirtualScoutingSettings.h`）

```cpp
// 获取项目设置实例（单例）
UVirtualScoutingSettings* Settings = UVirtualScoutingSettings::GetVirtualScoutingSettings();
if (Settings)
{
    // 检查是否使用英制单位
    bool bIsImperial = Settings->bUseImperial;
    
    // 获取可用的光圈列表
    const TArray<float>& Apertures = Settings->ViewfinderApertureArray;
    
    // 修改生成Actor后的工具行为（在内存中，需保存以持久化）
    Settings->bSwapToGrabToolOnSpawnNewActor = false;
    Settings->TryUpdateDefaultConfigFile(); // 尝试保存到配置文件
}
```

### 进阶用法

同时访问项目设置和用户个人设置，动态调整用户体验。
（来源：`Public/VirtualScoutingSettings.h`）

```cpp
// 假设在某个管理VR体验的类中
void AdjustVRComfort(float NewFlightSpeed, bool bSmoothRotation)
{
    // 修改用户个人设置
    UVirtualScoutingEditorSettings* UserSettings = UVirtualScoutingEditorSettings::GetVirtualScoutingEditorSettings();
    if (UserSettings)
    {
        UserSettings->FlightSpeed = FMath::Clamp(NewFlightSpeed, 1.0f, 10.0f);
        UserSettings->bUseSmoothRotation = bSmoothRotation;
        UserSettings->TryUpdateDefaultConfigFile(); // 保存到用户配置
    }
    
    // 同时，你可能还需要根据用户设置调整项目的镜头参数
    UVirtualScoutingSettings* ProjectSettings = UVirtualScoutingSettings::GetVirtualScoutingSettings();
    if (ProjectSettings && bSmoothRotation)
    {
        // 示例：如果用户选择平滑旋转，可以为其默认视图查找器曝光补偿值做一点微调
        ProjectSettings->ViewfinderExposureCompensation = FMath::Lerp(1.0f, 0.5f, 0.3f);
        // 注意：通常不建议在运行时随意修改项目设置，这里仅为演示
    }
}
```

## Demo 示例

一个最小示例，展示如何在 C++ 中集成 Virtual Scouting 设置。

**VirtualScoutingManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VirtualScoutingManager.generated.h"

UCLASS()
class YOURPROJECT_API AVirtualScoutingManager : public AActor
{
    GENERATED_BODY()
    
public:
    AVirtualScoutingManager();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Virtual Scouting")
    void ConfigureForDirector();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Config")
    bool bUseMetricForDirector = true;
};
```

**VirtualScoutingManager.cpp**
```cpp
#include "VirtualScoutingManager.h"
#include "VirtualScoutingSettings.h"

AVirtualScoutingManager::AVirtualScoutingManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AVirtualScoutingManager::BeginPlay()
{
    Super::BeginPlay();
    ConfigureForDirector();
}

void AVirtualScoutingManager::ConfigureForDirector()
{
    // 确保插件设置已加载
    UVirtualScoutingSettings* Settings = UVirtualScoutingSettings::GetVirtualScoutingSettings();
    UVirtualScoutingEditorSettings* EditorSettings = UVirtualScoutingEditorSettings::GetVirtualScoutingEditorSettings();
    
    if (Settings && EditorSettings)
    {
        // 根据导演偏好设置单位制
        Settings->bUseImperial = !bUseMetricForDirector;
        
        // 为导演配置更舒适的飞行体验
        EditorSettings->FlightSpeed = 6.0f;
        EditorSettings->bUseSmoothRotation = true;
        EditorSettings->bEnableTooltips = true;
        
        UE_LOG(LogVirtualScouting, Log, TEXT("Virtual Scouting configured for director: %s units, Smooth rotation enabled."),
            bUseMetricForDirector ? TEXT("Metric") : TEXT("Imperial"));
    }
}
```

## 模块依赖

从各模块的 Build.cs 分析，使用本插件时，你的模块可能需要添加以下依赖（省略了 Core, Engine 等通用模块）：

| 模块 | 用途 |
|---|---|
| `CinematicCamera` | 用于操作和模拟电影级摄像机参数 |
| `Foliage` | 可能与场景中的植被交互或放置相关 |
| `InputCore` | 处理输入核心功能，特别是针对VR控制器 |
| `VREditor` | 提供UE编辑器VR会话的基础框架和工具 |
| `OpenXR` | 集成OpenXR标准，支持广泛的VR头显设备 |
| `HeadMountedDisplay` | 与头戴式显示器硬件交互的核心接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数可能产生警告的代码。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符，确保其与32位或64位参数匹配，避免未定义行为。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏UE_LOG迁移到新版UE_LOGF，进行现代化更新。 |
| 2026-03-13 | `b1da5d8f` | [Gizmos] Remove GizmoEdMode from areas not covered by preflight checks | [ Gizmos ] 从预检查未覆盖的区域移除了GizmoEdMode引用，清理代码。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件模板从 Base<Plugin>.ini 重命名为标准的 Default<Plugin>.ini。 |

### 维护评价

Virtual Scouting 插件**创建于2024年9月**，相对年轻。最近的提交记录（截至2026年5月）显示，它仍在**持续维护中**，但近期的更新主要是**编译器警告修复、日志系统现代化和代码清理**等基础维护工作，而非重大新功能开发。这表明该插件已经达到了一个相对稳定的状态。

考虑到它已从实验性状态毕业，并正式归类于“Virtual Production”文件夹，其核心功能是完整且可用的。对于正在进行或计划进行虚拟制片预可视化的团队，这是一个**值得推荐使用的官方工具**。然而，用户应意识到，如果遇到复杂的交互问题或需要高级功能，可能需要依赖社区或等待Epic未来的更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting)
- 官方文档：未在 `.uplugin` 中提供
- 测试用例：在提供的源码信息中未发现测试文件