# Mesh Terrain Mode

> Mesh Terrain Mode includes a suite of interactive tools for creating and editing Mesh Partitions in the Editor

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshTerrainMode` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshTerrainMode) | |

## 用途

Mesh Terrain Mode 是一个编辑器模式插件，提供了一套完整的交互式工具集，用于在编辑器中创建和编辑 **Mesh Partitions（网格分区）**。它本质上是一个基于 Mesh 的地形编辑系统，与传统的基于高度图的地形系统不同，它直接操作网格几何体。

该插件解决的核心问题是：**需要一种可视化、交互式的方式来对网格表面进行雕刻、绘制、创建和编辑操作**，类似于传统地形工具但作用于任意网格表面。它提供了多个子模式（Submode）来组织不同类型的工具：

- **Sculpt（雕刻）**：对网格表面进行顶点级别的雕刻操作
- **Shapes（形状）**：创建基础几何体（盒子、圆柱、球体等）
- **Edit（编辑）**：多边形编辑、细分、变形等网格编辑操作
- **Create（创建）**：创建新的网格资产
- **Paint（绘制）**：在网格表面绘制属性
- **Modifiers（修改器）**：应用修改器效果

该插件还支持数位板压力感应输入，适合使用绘图板进行精细的地形雕刻工作。

## 使用场景

- 你需要在 UE5 中创建基于网格的地形系统，而非传统高度图地形 → 用 Mesh Terrain Mode
- 你需要对网格表面进行交互式雕刻（类似 ZBrush 风格）→ 用 Sculpt 子模式
- 你需要快速创建基础几何体并组合成地形 → 用 Shapes 子模式
- 你需要在网格表面绘制材质层或属性 → 用 Paint 子模式
- 你需要使用数位板进行压力感应雕刻 → 该插件内置 StylusInput 支持

## 蓝图用法

该插件主要是一个编辑器模式（Editor Mode），大部分功能通过编辑器 UI 交互完成，而非蓝图节点。以下是可访问的设置类：

### 核心设置类

| 类 | 说明 |
|---|---|
| `UMeshTerrainModeSettings` | 插件全局设置，配置资产生成行为、默认网格对象类型等 |
| `UMeshTerrainModeEditableToolPaletteConfig` | 工具面板配置，存储用户自定义的工具面板布局 |

### 设置枚举

| 枚举 | 说明 |
|---|---|
| `EMeshTerrainModeDefaultMeshObjectType` | 默认网格对象类型：StaticMeshAsset / VolumeActor / DynamicMeshActor |
| `EMeshTerrainModeAssetGenerationBehavior` | 资产生成行为：自动保存 / 仅标记修改 / 交互式提示保存 |
| `EMeshTerrainModeAssetGenerationLocation` | 资产生成位置：世界相对路径 / 全局路径 / 当前浏览器路径 |

## C++ 用法

### 头文件引入

```cpp
#include "MeshTerrainMode.h"
#include "MeshTerrainModeSettings.h"
#include "MeshTerrainModeModule.h"
```

### 基本用法：注册自定义工具扩展

该插件通过 `IMeshTerrainModeToolExtension` 接口支持第三方工具扩展。你可以实现该接口来向 Mesh Terrain Mode 添加自定义工具和子模式。

```cpp
// Source: Source/MeshTerrainMode/Private/MeshTerrainModeToolExtensions.h

#include "MeshTerrainModeToolExtensions.h"

// 实现工具扩展接口，向 Mesh Terrain Mode 注册自定义工具
class FMyMeshTerrainToolExtension : public IMeshTerrainModeToolExtension
{
public:
    // 返回要添加到现有子模式的工具列表
    virtual TArray<FExtensionSubmodeDescription> GetExtensionSubmodes() const override
    {
        TArray<FExtensionSubmodeDescription> Submodes;
        // 添加自定义子模式
        FExtensionSubmodeDescription Desc;
        Desc.MakeNewSubmode = []() -> TSharedPtr<UE::MeshTerrain::FSubmode>
        {
            // 创建并返回自定义子模式
            return nullptr;
        };
        Submodes.Add(Desc);
        return Submodes;
    }

    // 返回要添加到工具面板的自定义工具
    virtual TArray<FExtensionToolDescription> GetExtensionTools() const override
    {
        TArray<FExtensionToolDescription> Tools;
        // 添加自定义工具描述
        return Tools;
    }
};
```

### 进阶用法：资产生成工具函数

```cpp
// Source: Source/MeshTerrainMode/Private/MeshTerrainModeAssetUtils.h

#include "MeshTerrainModeAssetUtils.h"

// 获取新资产的路径和名称
FString AssetPath = UE::MeshTerrain::GetNewAssetPathName(
    TEXT("MyTerrainMesh"),  // 基础名称
    GetWorld(),             // 目标世界
    TEXT("/Game/Terrain/")  // 建议文件夹
);

// 资产创建后的自动保存处理
UObject* NewAsset = /* 创建的资产 */;
UE::MeshTerrain::OnNewAssetCreated(NewAsset);
```

### 进阶用法：自定义属性面板

```cpp
// Source: Source/MeshTerrainMode/Private/MeshTerrainDetailCustomizations.h

#include "MeshTerrainDetailCustomizations.h"

// 注册自定义属性面板定制
class FMyPropertyCustomization : public UE::MeshTerrain::IMeshTerrainPropertyCustomization
{
public:
    static TSharedRef<IMeshTerrainPropertyCustomization> MakeInstance()
    {
        return MakeShared<FMyPropertyCustomization>();
    }

    // 返回需要自定义 Widget 的属性
    virtual TMap<FName, UE::MeshTerrain::FMeshTerrainCustomizationData> GetCustomizationData() override
    {
        TMap<FName, UE::MeshTerrain::FMeshTerrainCustomizationData> Data;
        // 为特定属性注册自定义 Widget
        return Data;
    }

    // 返回需要编辑条件的属性
    virtual TMap<FName, UE::MeshTerrain::FMeshTerrainEditConditionData> GetEditConditionData() override
    {
        TMap<FName, UE::MeshTerrain::FMeshTerrainEditConditionData> Conditions;
        return Conditions;
    }
};

// 在模块启动时注册
UE::MeshTerrain::FMeshTerrainDetailCustomizations::RegisterCustomization(
    FName("MySection"),
    FMyPropertyCustomization::MakeInstance()
);
```

## Demo 示例

以下示例展示如何创建一个自定义的 Mesh Terrain 工具扩展插件：

```cpp
// MyMeshTerrainExtension.h
#pragma once

#include "MeshTerrainModeToolExtensions.h"

class FMyMeshTerrainExtension : public IMeshTerrainModeToolExtension
{
public:
    virtual ~FMyMeshTerrainExtension() = default;

    // IModelingModeToolExtension 接口
    virtual FText GetExtensionName() const override
    {
        return FText::FromString(TEXT("My Custom Extension"));
    }

    virtual TArray<FExtensionToolDescription> GetExtensionTools() const override
    {
        TArray<FExtensionToolDescription> Tools;
        // 注册自定义工具
        return Tools;
    }

    // IMeshTerrainModeToolExtension 接口
    virtual TArray<FExtensionSubmodeDescription> GetExtensionSubmodes() const override
    {
        TArray<FExtensionSubmodeDescription> Submodes;
        return Submodes;
    }
};
```

```cpp
// MyMeshTerrainExtension.cpp
#include "MyMeshTerrainExtension.h"

// 注册为模块化特性，Mesh Terrain Mode 会自动发现并加载
void RegisterMyExtension()
{
    FMyMeshTerrainExtension* Extension = new FMyMeshTerrainExtension();
    IModularFeatures::Get().RegisterModularFeature(
        IMeshTerrainModeToolExtension::GetModularFeatureName(),
        Extension
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelingToolsEditorMode` | 建模工具编辑器模式基础框架（工具扩展接口来源） |
| `InteractiveToolsFramework` | 交互式工具框架 |
| `GeometryFramework` | 几何体框架（DynamicMesh 等） |
| `GeometrySelectionManager` | 几何体选择管理 |
| `ToolWidgets` | 工具 UI 组件（SDraggableBoxOverlay 等） |
| `StylusInput` | 数位板压力感应输入（条件编译） |

## 维护状态

### 近期更新

```
- 2026-04-24 f907e2ba MeshTerrain: Replaced SubmodeToolPanel SSplitter based resize implementation with SDraggableBoxOverlay
- 2026-04-24 473e05b1 Mesh Terrain sculpt layer tools
- 2026-04-24 4103499c Mesh Terrain: allow level editor gizmos to show while UHeightSculptTool is active
```

### 维护评价

该插件是一个**全新的实验性插件**，创建于 2026 年 4 月 23 日，距今不到 1 天。从 git 历史来看，它正处于**密集开发阶段**，最近的提交涵盖了 UI 重构（从 SSplitter 迁移到 SDraggableBoxOverlay）、新工具功能（sculpt layer tools）和编辑器集成改进（gizmo 显示）。

**注意事项**：
- ⚠️ 标记为实验性（Experimental），API 可能会发生重大变化
- ⚠️ 默认未启用，需要在插件设置中手动启用
- 该插件仍在快速迭代中，不建议在生产环境中使用
- 作为 Mesh Partition 分类下的新系统，它可能是 UE5 未来地形系统的重要组成部分

**推荐**：适合早期体验和原型开发，不建议用于正式项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshTerrainMode)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain#meshterrainmode)