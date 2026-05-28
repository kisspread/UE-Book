# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏相机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 插件提供了一套完整的、模块化且数据驱动的相机系统，旨在替代或补充 Unreal Engine 中传统的相机机制。它通过**资产化**和**节点图编辑器**的方式，让设计师和开发者能够以可视化、非线性、组合式的方式构建复杂的相机行为，而无需编写大量底层逻辑代码。

该系统解决的核心问题是：
1.  **复杂性管理**：传统相机逻辑容易变得混乱且难以维护。此系统将相机行为分解为可复用的“相机装备（Camera Rigs）”，并允许它们通过“相机资产（Camera Assets）”进行组合。
2.  **数据驱动**：相机配置存储在数据资产中，便于版本控制、复制和热重载。
3.  **扩展性**：提供了基础的节点图框架（Object Tree Graph），允许开发者通过添加自定义节点类型来扩展系统功能。

简而言之，如果你的项目需要高度定制化、可配置且复杂的相机系统（例如第三人称动作游戏、电影化过场动画），并且希望减少C++编码量、更多依赖蓝图/编辑器工具，那么这个系统是你的理想选择。

## 使用场景

- **制作复杂的相机行为**：当你需要在一个相机镜头内实现多种效果（如跟随、变焦、抖动、看向特定目标）的平滑过渡和混合时，可以使用 `CameraAsset` 和 `CameraRigAsset` 在节点图中进行设计。
- **需要运行时动态相机效果**：通过 `CameraShakeAsset` 创建可参数化、可叠加的相机抖动效果。
- **在编辑器中预览和调试相机**：插件提供了丰富的编辑器工具和调试器，允许你在PIE（Play In Editor）中实时观察和调整相机行为。
- **项目需要大量风格迥异的相机配置**：例如在开放世界游戏中，不同区域（城镇、地牢、野外）可能需要不同的基础相机设置，数据资产的方式使其易于管理和切换。

## 蓝图用法

此插件的运行时蓝图API主要暴露在 `GameplayCameras` 模块中。由于用户提供的主要是编辑器模块（`GameplayCamerasEditor`）的源码，以下蓝图节点基于编辑器模块的公开接口推断，用于在编辑器中与相机资产交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Camera Asset Editor` | 为指定的相机资产创建并打开一个编辑器实例 | `IGameplayCamerasEditorModule` |
| `Create Camera Rig Editor` | 为指定的相机装备资产创建并打开一个编辑器实例 | `IGameplayCamerasEditorModule` |
| `Create Camera Shake Editor` | 为指定的相机摇晃资产创建并打开一个编辑器实例 | `IGameplayCamerasEditorModule` |
| `Create Camera Variable Collection Editor` | 为指定的相机变量集合创建并打开一个编辑器实例 | `IGameplayCamerasEditorModule` |
| `Register Debug Category` | 向相机调试器注册一个新的调试分类，可用于过滤和显示信息 | `IGameplayCamerasEditorModule` |

### 使用示例（蓝图描述）

假设你有一个 `UCameraAsset` 变量 `MyCameraAsset`，你想在编辑器中打开它的编辑界面：

1.  在蓝图图表中，使用 `IGameplayCamerasEditorModule::Get()` 节点获取编辑器模块的单例。
2.  将 `MyCameraAsset` 变量连接到 `Create Camera Asset Editor` 节点的 `CameraAsset` 引脚。
3.  对于 `Mode`，通常选择 `Standalone` 或 `WorldCentric`。
4.  执行此蓝图即可打开相机资产编辑器窗口。

## C++ 用法

由于没有提供具体的测试用例文件，以下用法基于提供的接口头文件（特别是 `IGameplayCamerasEditorModule.h`）进行推断。

### 头文件引入

```cpp
#include “GameplayCamerasEditorModule.h” // 主要包含 IGameplayCamerasEditorModule
#include “IGameplayCamerasLiveEditManager.h” // 用于实时编辑功能
```

### 基本用法

以下示例展示了如何在编辑器工具或自定义UI中调用插件的编辑器功能。

```cpp
// 来源: Public/IGameplayCamerasEditorModule.h
// 获取编辑器模块的单例
UE::Cameras::IGameplayCamerasEditorModule& EditorModule = UE::Cameras::IGameplayCamerasEditorModule::Get();

// 创建一个相机装备资产的编辑器
UCameraRigAsset* MyRigAsset = ...; // 获取或创建一个相机装备资产
EditorModule.CreateCameraRigEditor(
    EToolkitMode::Standalone,
    TSharedPtr<IToolkitHost>(), // 在独立模式下可以为null
    MyRigAsset
);

// 向调试器注册一个自定义分类
UE::Cameras::FCameraDebugCategoryInfo CategoryInfo;
CategoryInfo.Name = TEXT(“MyCustomDebug”);
CategoryInfo.DisplayText = FText::FromString(TEXT(“我的调试信息”));
CategoryInfo.ToolTipText = FText::FromString(TEXT(“显示自定义的相机调试数据”));
// CategoryInfo.IconImage = ...; // 可设置图标
EditorModule.RegisterDebugCategory(CategoryInfo);
```

### 进阶用法

系统还提供了“实时编辑”管理器，用于监听资产或节点的变化并触发回调，这在实现编辑器预览功能时非常有用。

```cpp
// 来源: Private/GameplayCamerasLiveEditManager.h, Public/IGameplayCamerasLiveEditManager.h
// 获取实时编辑管理器（通常由编辑器工具包内部持有）
TSharedPtr<UE::Cameras::IGameplayCamerasLiveEditManager> LiveEditManager = ...;

// 假设我们有一个自定义的监听器类 FMyPreviewListener : public IGameplayCamerasLiveEditListener
FMyPreviewListener* Listener = new FMyPreviewListener();

// 监听特定资产包（例如一个 UCameraAsset 的包）的更改
UPackage* AssetPackage = MyCameraAsset->GetPackage();
LiveEditManager->AddListener(AssetPackage, Listener);

// 当资产被修改并重新构建时，LiveEditManager 会通知所有注册的监听器。
// 监听器可以实现 IGameplayCamerasLiveEditListener::NotifyPostBuildAsset() 来更新预览。
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在自定义的编辑器模块中集成 GameplayCameras 编辑器功能。

```cpp
// MyEditorModule.h
#pragma once
#include “Modules/ModuleManager.h”
#include “IGameplayCamerasEditorModule.h”

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // 一个用于打开相机资产的函数
    void OpenCameraAssetEditor(UCameraAsset* InAsset);
};
```

```cpp
// MyEditorModule.cpp
#include “MyEditorModule.h”
#include “CameraAsset.h” // 假设的相机资产头文件
#include “GameplayCamerasEditorModule.h” // GameplayCameras 编辑器模块

void FMyEditorModule::StartupModule()
{
    // 模块启动时可以进行一些初始化
}

void FMyEditorModule::ShutdownModule()
{
}

void FMyEditorModule::OpenCameraAssetEditor(UCameraAsset* InAsset)
{
    if (!InAsset) return;

    // 检查 GameplayCameras 编辑器模块是否加载
    if (UE::Cameras::IGameplayCamerasEditorModule::IsAvailable())
    {
        UE::Cameras::IGameplayCamerasEditorModule& EditorModule = UE::Cameras::IGameplayCamerasEditorModule::Get();
        // 在独立模式下创建编辑器
        EditorModule.CreateCameraAssetEditor(
            EToolkitMode::Standalone,
            TSharedPtr<IToolkitHost>(),
            InAsset
        );
    }
}
```

## 模块依赖

要使用 `GameplayCameras` 插件（特别是其编辑器功能），你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 插件依赖增强输入系统，用于处理相机输入 |
| `GameplayCameras` | 插件的核心运行时模块，包含相机资产类型和逻辑 |
| `GameplayCamerasEditor` | 插件的编辑器模块，提供资产编辑器、图表编辑器等工具 |

**注意**：如果你只使用运行时功能（如在蓝图中创建和使用相机资产），依赖 `GameplayCameras` 即可。如果你需要扩展编辑器或调用编辑器API（如上C++示例），则需要依赖 `GameplayCamerasEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复了在PIE中相机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，double常量转换为float时产生警告的代码 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为一些追踪通道添加或更新描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | （通用的插件更新提交，可能包含多项改动） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF格式 |

### 维护评价

- **维护状态**：**活跃维护中**。最近一次更新在2026年5月，且近期有多次提交，内容涉及功能修复（变量覆盖）、编译警告消除和追踪系统优化。
- **创建时间**：插件创建于约6年前，属于较成熟的功能模块。
- **实验性警告**：插件在 `.uplugin` 中标记为 `IsExperimentalVersion = true`，这意味着其API和功能在未来版本中可能发生重大变化，不建议在追求稳定性的项目核心功能中深度依赖。
- **推荐度**：推荐**有经验的团队**在**新项目**或**实验性功能**中评估和使用。它提供了强大的相机编辑能力，但需注意其“实验性”状态，做好应对API变动的准备。对于长期维护的项目，需要权衡其灵活性与潜在的升级成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]() （插件内未提供，暂无链接）
- [测试用例]() （插件目录内未发现专用测试文件，可能集成在引擎测试套件中）