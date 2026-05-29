# Virtual Camera

> Content for VirtualCameraCore which adds actors, components, and utilities for controlling and viewing cameras via physical devices.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、蓝图、材质等） |
| 模块 | `VCamExtensions` (Runtime), `VCamExtensionsEditor` (Runtime), `VirtualCamera` (Runtime), `VirtualCameraEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera) | |

## 用途

Virtual Camera 插件是 **Virtual Camera Core** 插件的**内容与编辑器扩展**集合。其主要目的是提供一套完整的资产、Actor、组件和编辑器工具，让用户能够**通过物理设备（如iPad、专业控制器）实时控制 Unreal Engine 中的虚拟相机**。它解决了虚拟制作（Virtual Production）流程中，如何将物理设备的输入无缝映射到引擎内相机参数（位置、旋转、焦距、光圈等）的问题，实现了对虚拟相机进行直观、实时的操控和预览。

## 使用场景

- **虚拟制作（VP）与虚拟勘景**：导演或摄影指导使用移动设备或物理控制器在实时渲染的虚拟场景中取景、构图。
- **影视预览与预演（Previz）**：快速迭代和预览复杂的相机运动与镜头设置。
- **游戏动画镜头制作**：通过物理设备辅助，为过场动画或实时序列创建更具表现力的相机轨迹。
- **现场直播与体育转播**：在虚拟演播室环境中，通过物理设备控制虚拟摄像机进行现场切换。

## 蓝图用法

当前文档描述的模块 `VCamExtensionsEditor` 主要提供**编辑器扩展**，用于创建和管理 VirtualCamera 相关的资产。它不直接暴露 `BlueprintCallable` 节点给运行时蓝图。核心的控制逻辑、Actor 和组件（如 `AVCamPlayerControllerManager`、`UVCamComponent`）位于其他关联模块（如 `VirtualCamera` 和 `VirtualCameraCore`）中。

### 编辑器资产创建

此模块注册了两个自定义资产类型，可在编辑器内容浏览器中通过右键菜单创建：
- **`UAssetDefinition_ModifierBoundWidgetStyles`**：定义了“修改器绑定的控件样式”资产，用于配置相机控制界面（UI）中各种控件的样式。
- **`UAssetDefinition_ModifierHierarchy`**：定义了“修改器层级”资产，用于组织和管理控制虚拟相机的各项参数（如位置、旋转、焦距）及其优先级。

## C++ 用法

此模块（`VCamExtensionsEditor`）为 C++ 开发者提供了**扩展编辑器功能**的接口，主要涉及自定义资产的工厂类。运行时的核心 API 不在此模块中。

### 头文件引入

使用此模块提供的资产工厂类，通常需要引入相关头文件：
```cpp
#include "Factories/ModifierBoundWidgetStylesAssetFactory.h"
#include "Factories/ModifierHierarchyAssetFactory.h"
```

### 基本用法

**示例：自定义资产工厂类结构（摘自源码）**

以下代码展示了 `VCamExtensionsEditor` 模块如何定义资产工厂，这些工厂决定了如何在编辑器中创建新的资产实例。开发者可以参照此模式为自己的虚拟制作资产类型创建工厂。

*来源: `Private/Factories/ModifierBoundWidgetStylesAssetFactory.h`*

```cpp
UCLASS()
class UModifierBoundWidgetStylesAssetFactory : public UFactory
{
    GENERATED_BODY()
public:
    UModifierBoundWidgetStylesAssetFactory();

    //~ Begin UFactory Interface
    virtual FText GetDisplayName() const override;
    virtual FText GetToolTip() const override;
    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent, FName Name, EObjectFlags Flags, UObject* Context, FFeedbackContext* Warn) override;
    virtual uint32 GetMenuCategories() const override;
    virtual const TArray<FText>& GetMenuCategorySubMenus() const override;
    //~ End UFactory Interface
};
```

**关键接口说明**：
- `FactoryCreateNew`：当用户在编辑器中右键选择“创建”时被调用，负责实例化新的资产对象。
- `GetMenuCategories` 和 `GetMenuCategorySubMenus`：定义新资产在编辑器“添加”菜单中所属的分类和子菜单路径。

### 进阶用法

对于希望深度集成到编辑器虚拟制作工具链中的 C++ 模块，通常需要：
1.  **依赖 `VCamExtensions` 模块**：以访问其提供的运行时核心资产类型和数据结构。
2.  **参照 `VCamExtensionsEditor` 模块**：实现自己的 `UFactory` 和 `UAssetDefinition` 类，以在编辑器中注册新的资产类型，并将其集成到特定的资产类别中（例如，与 `ModifierHierarchy` 资产协作）。

## Demo 示例

本模块（`VCamExtensionsEditor`）是编辑器扩展，不包含可直接运行的运行时示例。核心的运行时 Actor、组件和交互逻辑，请参考 `VirtualCamera` 和 `VirtualCameraCore` 模块。

一个最小的、启用此插件的项目，其 `Build.cs` 文件应包含以下依赖，以便访问该插件提供的核心资产类型：

*来源: 推断自 `VCamExtensionsEditor.build.cs` 的依赖*

```cpp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "VirtualCameraCore", // 核心资产类型与接口
    "VCamExtensions"    // 运行时扩展模块
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VirtualCameraCore` | 提供虚拟相机的核心资产类型、组件接口和基础逻辑。 |
| `AssetDefinition` | 用于实现自定义资产在内容浏览器中的显示与交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 重新组织虚拟制作资产分类，优化内容浏览器组织结构。 |
| 2026-04-20 | `9de9532f` | VCam: update transform track mask based on constraint filter | 根据约束过滤器更新变换轨道遮罩，增强了动画和约束功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`，这是引擎日志系统的更新。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的一次提交（CL51314860），可能修复了引入的问题。 |

### 维护评价

- **活跃维护**：插件在 2026 年内有多次功能性更新（如资产重组、约束功能改进），表明它仍在积极开发和优化中，以配合虚拟制作工作流。
- **Beta状态**：`.uplugin` 中标记为 `IsBetaVersion: true`，意味着其 API 和功能集可能还不稳定，在未来版本中可能发生变化。
- **从 Experimental 迁移**：创建记录显示该插件是从 `Plugins/Experimental` 目录移出的正式版本，这通常是功能趋于稳定的标志。
- **推荐使用**：如果你的项目涉及虚拟制作，特别是需要物理设备控制相机，**强烈推荐使用**此插件。它是 Epic 官方提供的专业工具链的核心部分，尽管处于 Beta 阶段，但已有实际应用和持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera)
- [官方文档](https://docs.unrealengine.com/) （请参考官方文档站内搜索 “Virtual Camera” 或 “Virtual Production”）