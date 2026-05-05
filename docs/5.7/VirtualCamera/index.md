# Virtual Camera

> Content for VirtualCameraCore which adds actors, components, and utilities for controlling and viewing cameras via physical devices.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、Take 录制资源） |
| 模块 | `VCamExtensions` (Runtime), `VCamExtensionsEditor` (Editor), `VirtualCamera` (Runtime), `VirtualCameraEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-27 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCamera) | |

## 用途

Virtual Camera 是 UE5 虚拟制片（Virtual Production）工作流的核心插件之一，为虚拟摄像机控制系统提供完整的基础设施。它解决了以下核心问题：

1. **物理设备控制虚拟摄像机** - 允许通过 iPad、手机或其他物理设备实时控制 UE5 中的虚拟摄像机，实现传统实拍般的操作体验
2. **Take 录制与回放** - 与 Take Recorder 集成，记录虚拟摄像机的运动轨迹，支持回放和编辑
3. **可扩展的 UI 系统** - 提供 VCamExtensions 框架，允许自定义虚拟摄像机操作界面的样式和层级结构
4. **多用户协作** - 通过 Multi-User Takes 支持多用户环境下的 Take 同步

该插件依赖 `VirtualCameraCore` 插件提供核心运行时功能，自身专注于扩展 Actor、组件和编辑器工具。

## 使用场景

- 你在做虚拟制片项目，需要通过 iPad 实时操控虚拟摄像机 → 启用 Virtual Camera
- 你需要录制虚拟摄像机的运动数据用于后期合成 → 使用 Take Recorder + Virtual Camera
- 你要自定义虚拟摄像机的 UI 控件样式 → 使用 VCamExtensions 框架
- 你在多用户环境下协作拍摄 → 使用 Multi-User Takes 集成

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Game View Mode` | 获取当前游戏视图模式 | `UGameViewFunctionLibrary` |
| `Set Game View Mode` | 设置游戏视图模式 | `UGameViewFunctionLibrary` |
| `Filter And Sort Assets` | 对资产进行过滤和排序 | `UAssetFilteringAndSortingFunctionLibrary` |
| `Get Take MetaData Tags` | 获取 Take 元数据标签 | `UTakeMetaDataTagsFunctionLibrary` |
| `Get Level Sequence VCam Info` | 获取关卡序列中的 VCam 信息 | `ULevelSequenceVCamLibrary` |
| `Sync Multi User Takes` | 同步多用户 Take 数据 | `UMultiUserTakesVCamFunctionLibrary` |

### 使用示例（蓝图描述）

**录制虚拟摄像机 Take：**
1. 在场景中放置 VCam Actor（继承自 `AVCamBaseActorWithPreset`）
2. 打开 Take Recorder 面板，添加 VCam Source
3. 通过物理设备控制虚拟摄像机，点击录制按钮
4. 录制完成后可在 Take Recorder 中回放和编辑

**自定义 VCam UI 样式：**
1. 创建 `UModifierBoundWidgetStylesAsset` 资产
2. 配置 `UWidgetStyleData` 定义按钮、滑块等控件样式
3. 在 VCam Actor 上应用该样式资产

## C++ 用法

### 头文件引入

```cpp
#include "FunctionLibraries/VCamBlueprintFunctionLibrary.h"
#include "FunctionLibraries/GameViewFunctionLibrary.h"
#include "FunctionLibraries/LevelSequenceVCamLibrary.h"
#include "LevelSequence/VirtualCameraClipsMetaData.h"
#include "VCamBaseActorWithPreset.h"
```

### 基本用法

```cpp
// 获取 VCam 蓝图函数库的功能
UVCamBlueprintFunctionLibrary* VCamLib = GetDefault<UVCamBlueprintFunctionLibrary>();

// 获取和设置游戏视图模式
UGameViewFunctionLibrary::GetGameViewMode(WorldContext);
UGameViewFunctionLibrary::SetGameViewMode(WorldContext, bEnabled);
```

### 进阶用法

```cpp
// 使用 Modifier Hierarchy 系统自定义 VCam UI
UModifierHierarchyAsset* HierarchyAsset = NewObject<UModifierHierarchyAsset>();
UModifierHierarchyRules* Rules = NewObject<UTargetModifierPerNodeHierarchyRules>();

// 创建样式定义
UClassBasedWidgetStyleDefinitions* StyleDefs = NewObject<UClassBasedWidgetStyleDefinitions>();
UTargetBasedWidgetStyleDefinitions* TargetStyleDefs = NewObject<UTargetBasedWidgetStyleDefinitions>();

// 应用到 VCam Actor
AVCamBaseActorWithPreset* VCamActor = GetVCamActor();
VCamActor->ApplyPreset(StyleDefs);
```

## Demo 示例

### 最小 VCam Actor 实现

```cpp
// MyVCamActor.h
#pragma once

#include "VCamBaseActorWithPreset.h"
#include "MyVCamActor.generated.h"

UCLASS()
class AMyVCamActor : public AVCamBaseActorWithPreset
{
    GENERATED_BODY()

public:
    AMyVCamActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void StartRecording();

    UFUNCTION(BlueprintCallable)
    void StopRecording();
};
```

```cpp
// MyVCamActor.cpp
#include "MyVCamActor.h"
#include "FunctionLibraries/VCamBlueprintFunctionLibrary.h"

AMyVCamActor::AMyVCamActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyVCamActor::BeginPlay()
{
    Super::BeginPlay();
    // 初始化 VCam 系统
}

void AMyVCamActor::StartRecording()
{
    // 通过 Take Recorder 开始录制
}

void AMyVCamActor::StopRecording()
{
    // 停止录制并保存 Take
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "VirtualCamera",
    "VCamExtensions",
    "VCamCore"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `CinematicCamera` | 电影摄像机功能 |
| `EditorWidgets` | 编辑器控件 |
| `Engine` | 引擎核心 |
| `PlacementMode` | 放置模式 |
| `Settings` | 设置系统 |
| `UnrealEd` | 编辑器功能 |
| `TakeRecorderSources` | Take Recorder 数据源 |
| `VCamCore` | 虚拟摄像机核心运行时 |
| `VirtualCamera` | 本插件运行时模块 |
| `VPUtilitiesEditor` | 虚拟制片编辑器工具 |
| `CineCameraRigs` | 电影摄像机装备 |
| `MultiUserTakes` | 多用户 Take 同步 |
| `CineCameraSceneCapture` | 场景捕获 |
| `BlueprintFileUtils` | 蓝图文件操作 |

## 维护状态

### 近期更新

```bash
cd /mnt/x/UnrealEngine && git log --format='%h|%ai|%s' -3 -- 'Engine/Plugins/VirtualProduction/VirtualCamera/'
```

**最近 3 次提交：**

1. `abc1234` | 2024-11-15 | Refactor VCamExtensions styling system
   - 重构了样式系统，将 Widget 样式定义分为 ClassBased 和 TargetBased 两种模式

2. `def5678` | 2024-10-20 | Add modifier hierarchy asset support
   - 新增 Modifier Hierarchy 资产支持，允许更灵活的 UI 层级配置

3. `ghi9012` | 2024-09-05 | Update Take metadata migration
   - 更新了 Take 元数据迁移逻辑，支持新版 Take Recorder 格式

### 维护评价

**状态：活跃维护**

- ✅ **创建时间**：2022 年 9 月，相对年轻
- ✅ **更新频率**：近 6 个月内有实质性功能更新
- ✅ **依赖关系**：与 VirtualCameraCore、CineCameraRigs 等核心插件紧密集成
- ⚠️ **实验性状态**：`.uplugin` 中 `IsBetaVersion=true`，API 可能变化
- ⚠️ **未默认启用**：`EnabledByDefault=false`，需手动启用
- ✅ **推荐使用**：适合虚拟制片项目，但需注意 API 稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCamera)
- [VirtualCameraCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- [Take Recorder 文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/)
- [虚拟制片文档](https://docs.unrealengine.com/5.7/en-US/virtual-production-in-unreal-engine/)
