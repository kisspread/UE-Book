# UVEditor

> Asset editor for modifying the UV mapping of a mesh

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产、材质模板） |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-21 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor) | |

## 用途

UVEditor 是 Unreal Engine 内置的 **UV 编辑器**，为网格体提供完整的 UV 映射编辑能力。它解决的核心问题是：在 UE 内部直接对 Static Mesh / Skeletal Mesh 的 UV 通道进行查看、修改和优化，无需导出到外部 DCC 工具（如 Blender、Maya）再重新导入。

该插件提供了一个独立的资产编辑器窗口，包含以下核心功能：

- **UV 展开与参数化**：支持 UVAtlas、XAtlas、PatchBuilder 三种自动展开算法，可一键生成 UV
- **Seam 编辑**：交互式地在网格体上绘制/删除 UV 接缝线，控制 UV 岛的切割方式
- **UV 变换工具**：平移、旋转、缩放 UV 岛，支持对齐（Align）和分布（Distribute）操作
- **多 UV 通道支持**：可编辑网格体的多个 UV 通道（UV Channel 0-7）
- **实时预览**：编辑过程中实时显示 UV 变换效果

## 使用场景

- 你的项目需要为 Static Mesh 生成或修复 UV 映射，但不想离开 UE 编辑器 → 用 UVEditor
- 你需要为光照烘焙（Lightmap）创建第二套 UV 通道 → 用 UVEditor 的自动参数化功能
- 你导入的模型 UV 有重叠或拉伸，需要在引擎内快速调整 → 用 UVEditor 的变换和对齐工具
- 你需要精确控制 UV 接缝位置来优化纹理采样 → 用 UVEditor 的 Seam 工具

## 模块概览

本插件由三个模块组成，职责分明：

| 模块 | 类型 | 职责 |
|---|---|---|
| `UVEditor` | Editor | 核心编辑器框架：编辑器窗口、资产交互、场景管理、工具管理器 |
| `UVEditorTools` | Editor | UV 编辑工具集：变换、对齐、分布、接缝、参数化等工具的运行时逻辑 |
| `UVEditorToolsEditorOnly` | Editor | 仅编辑器工具：属性面板自定义（Detail Customization）、参数化网格工具等 |

### 子模块文档

- [UVEditorToolsEditorOnly](UVEditorToolsEditorOnly.md) — 属性面板自定义与参数化工具

> ⚠️ `UVEditor` 和 `UVEditorTools` 模块的详细文档需要单独生成（源码量较大）。

## 蓝图用法

UVEditor 是纯编辑器插件，不暴露 BlueprintCallable 节点供运行时使用。其交互完全通过编辑器 UI 完成：

1. 在 Content Browser 中右键点击 Static Mesh 资产
2. 选择 **"UV Editor"** 打开 UV 编辑器窗口
3. 在工具栏中选择所需的 UV 工具（Transform、Seam、Parameterize 等）
4. 在 3D 视口和 UV 视口中交互编辑

## C++ 用法

### 头文件引入

```cpp
#include "UVEditorToolMeshInput.h"
#include "UVEditorParameterizeMeshTool.h"
```

### 基本用法 — 自动参数化网格 UV

从 `UUVEditorParameterizeMeshTool` 的接口可以看到，参数化工具支持多种展开算法：

```cpp
// 创建参数化工具构建器
UUVEditorParameterizeMeshToolBuilder* Builder = NewObject<UUVEditorParameterizeMeshToolBuilder>();

// 设置目标网格体输入
Builder->Targets = &MeshInputTargets;

// 构建工具实例
UUVEditorParameterizeMeshTool* Tool = Cast<UUVEditorParameterizeMeshTool>(
    Builder->BuildTool(ToolBuilderState)
);

// 工具内部会根据 Settings 中选择的方法类型自动切换：
// - UVAtlas: 基于微软 UVAtlas 库的展开算法
// - XAtlas: 快速自动展开
// - PatchBuilder: 基于 Patch 的展开方式
```

### 进阶用法 — 属性面板自定义

UVEditorToolsEditorOnly 模块提供了多个 `IDetailCustomization` 实现，用于自定义工具属性面板的显示：

```cpp
#include "DetailsCustomizations/UVTransformToolCustomizations.h"
#include "DetailsCustomizations/UVEditorSeamToolCustomizations.h"

// 注册自定义属性面板（通常在模块 StartupModule 中）
FPropertyEditorModule& PropertyModule = 
    FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

// UV 变换工具的属性面板自定义
PropertyModule.RegisterCustomClassLayout(
    UUVEditorUVTransformProperties::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FUVEditorUVTransformToolDetails::MakeInstance
    )
);

// Seam 工具的属性面板自定义
PropertyModule.RegisterCustomClassLayout(
    UUVEditorSeamToolProperties::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FUVEditorSeamToolPropertiesDetails::MakeInstance
    )
);

// 对齐工具的属性面板自定义
PropertyModule.RegisterCustomClassLayout(
    UUVEditorUVAlignProperties::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FUVEditorUVAlignToolDetails::MakeInstance
    )
);

// 分布工具的属性面板自定义
PropertyModule.RegisterCustomClassLayout(
    UUVEditorUVDistributeProperties::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FUVEditorUVDistributeToolDetails::MakeInstance
    )
);
```

## Demo 示例

以下展示如何在自定义编辑器工具中集成 UV 参数化功能：

```cpp
// MyUVHelper.h
#pragma once

#include "CoreMinimal.h"
#include "UVEditorToolMeshInput.h"
#include "UVEditorParameterizeMeshTool.h"

class FMyUVHelper
{
public:
    // 对一组网格体输入执行自动 UV 参数化
    static bool AutoParameterizeUVs(
        const TArray<TObjectPtr<UUVEditorToolMeshInput>>& Targets,
        EUVParameterizeMethod Method = EUVParameterizeMethod::UVAtlas
    );
};
```

```cpp
// MyUVHelper.cpp
#include "MyUVHelper.h"
#include "UVEditorParameterizeMeshTool.h"

bool FMyUVHelper::AutoParameterizeUVs(
    const TArray<TObjectPtr<UUVEditorToolMeshInput>>& Targets,
    EUVParameterizeMethod Method)
{
    if (Targets.Num() == 0)
    {
        return false;
    }

    // 创建工具构建器
    UUVEditorParameterizeMeshToolBuilder* Builder = 
        NewObject<UUVEditorParameterizeMeshToolBuilder>();
    Builder->Targets = &Targets;

    // 验证是否可以构建工具
    FToolBuilderState SceneState;
    if (!Builder->CanBuildTool(SceneState))
    {
        return false;
    }

    // 构建并配置工具
    UUVEditorParameterizeMeshTool* Tool = 
        Cast<UUVEditorParameterizeMeshTool>(Builder->BuildTool(SceneState));
    
    if (!Tool)
    {
        return false;
    }

    Tool->SetTargets(Targets);
    Tool->Setup();

    // 设置参数化方法
    // Tool->Settings->MethodType = Method;  // 通过属性修改触发重新计算

    // 执行参数化（工具会在 OnTick 中异步处理）
    // 实际使用中需要通过工具管理器的 Tick 循环驱动

    return true;
}
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GeometryProcessing` | 几何处理算法库，提供 UVAtlas、网格体参数化等底层算法 |
| `MeshModelingToolset` | 网格体建模工具集，提供交互式工具框架和基础建模操作 |
| `MeshModelingToolsetExp` | 实验性建模工具集，提供额外的实验性工具支持 |

### 模块依赖（UVEditorToolsEditorOnly）

无特殊依赖（仅标准 Core/Engine/Slate 等），额外依赖 `UVEditorTools` 模块。

## 维护状态

### 近期更新

```
- febd61e82650 UVEditor: Fixed localization issue for the "Advanced Transform" category label.
  → 修复了"Advanced Transform"分类标签的本地化问题
- 8396b185774c Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n
  → 批量更新头文件的 DLL 导出宏，确保 dllstorage 标注在方法/静态变量上而非类型上
- e7531e777492 UVEditor: Fix the localization support for the Transform tool's Advanced Transform category name.
  → 修复 Transform 工具"Advanced Transform"分类名称的本地化支持
```

### 维护评价

- **状态**：活跃维护中
- **创建时间**：2021 年 4 月，约 4 年历史
- **近期更新**：最近的提交集中在本地化修复和代码质量改进，表明插件功能已趋于稳定
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，说明 Epic 仍将其视为 Beta 状态
- **推荐程度**：✅ 推荐使用。作为 UE 内置的 UV 编辑解决方案，它已具备完整的 UV 编辑能力。虽然标记为 Beta，但默认启用且持续维护，适合日常 UV 编辑工作。对于复杂的 UV 展开需求，建议结合外部 DCC 工具使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/uv-editor-in-unreal-engine/)（UE 官方 UV Editor 文档）

---

# UVEditorToolsEditorOnly 模块

> 编辑器专属的 UV 工具扩展，包含属性面板自定义和参数化网格工具

## 模块概述

`UVEditorToolsEditorOnly` 是 UVEditor 插件中负责**编辑器 UI 定制**和**高级工具实现**的模块。它包含：

1. **Detail Customization（属性面板自定义）**：为各 UV 工具的属性面板提供自定义 UI，包括按钮式模式切换、快捷操作菜单等
2. **ParameterizeMeshTool（参数化网格工具）**：自动 UV 展开工具，支持三种算法

## 核心组件

### 属性面板自定义类

| 类名 | 自定义目标 | 功能 |
|---|---|---|
| `FUVEditorSeamToolPropertiesDetails` | `UUVEditorSeamToolProperties` | Seam 工具的模式切换 UI |
| `FUVEditorUVTransformToolDetails` | `UUVEditorUVTransformProperties` | 变换工具的快捷平移/旋转菜单 |
| `FUVEditorUVQuickTransformToolDetails` | `UUVEditorUVQuickTransformProperties` | 快速变换工具（继承自 Transform） |
| `FUVEditorUVDistributeToolDetails` | `UUVEditorUVDistributeProperties` | 分布工具的模式按钮和手动距离控制 |
| `FUVEditorUVAlignToolDetails` | `UUVEditorUVAlignProperties` | 对齐工具的方向模式按钮 |

### 参数化工具类

| 类名 | 功能 |
|---|---|
| `UUVEditorParameterizeMeshToolBuilder` | 工具构建器，验证输入并创建工具实例 |
| `UUVEditorParameterizeMeshTool` | 自动 UV 参数化工具，支持 UVAtlas / XAtlas / PatchBuilder |

## C++ 用法

### 头文件引入

```cpp
#include "UVEditorToolsEditorOnlyModule.h"
#include "UVEditorParameterizeMeshTool.h"
#include "DetailsCustomizations/UVTransformToolCustomizations.h"
#include "DetailsCustomizations/UVEditorSeamToolCustomizations.h"
```

### 注册属性面板自定义

```cpp
// 在模块 StartupModule 中注册
void FUVEditorToolsEditorOnlyModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = 
        FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    // 注册 Seam 工具属性自定义
    PropertyModule.RegisterCustomClassLayout(
        TEXT("UVEditorSeamToolProperties"),
        FOnGetDetailCustomizationInstance::CreateStatic(
            &FUVEditorSeamToolPropertiesDetails::MakeInstance)
    );

    // 注册变换工具属性自定义（含快捷平移/旋转菜单）
    PropertyModule.RegisterCustomClassLayout(
        TEXT("UVEditorUVTransformProperties"),
        FOnGetDetailCustomizationInstance::CreateStatic(
            &FUVEditorUVTransformToolDetails::MakeInstance)
    );

    // 注册分布工具属性自定义（含模式按钮）
    PropertyModule.RegisterCustomClassLayout(
        TEXT("UVEditorUVDistributeProperties"),
        FOnGetDetailCustomizationInstance::CreateStatic(
            &FUVEditorUVDistributeToolDetails::MakeInstance)
    );

    // 注册对齐工具属性自定义（含方向按钮）
    PropertyModule.RegisterCustomClassLayout(
        TEXT("UVEditorUVAlignProperties"),
        FOnGetDetailCustomizationInstance::CreateStatic(
            &FUVEditorUVAlignToolDetails::MakeInstance)
    );
}

void FUVEditorToolsEditorOnlyModule::ShutdownModule()
{
    // 注销所有自定义
    if (FModuleManager::Get().IsModuleLoaded("PropertyEditor"))
    {
        FPropertyEditorModule& PropertyModule = 
            FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
        
        for (const FName& ClassName : ClassesToUnregisterOnShutdown)
        {
            PropertyModule.UnregisterCustomClassLayout(ClassName);
        }
    }
}
```

### 参数化工具使用

```cpp
// 参数化工具的核心接口
UUVEditorParameterizeMeshTool* Tool = /* 由 Builder 创建 */;

// 设置目标网格体
TArray<TObjectPtr<UUVEditorToolMeshInput>> Targets;
Targets.Add(MeshInput);
Tool->SetTargets(Targets);

// 初始化工具（创建预览、加载属性）
Tool->Setup();

// 工具生命周期
// - OnTick(): 每帧更新，处理异步计算结果
// - OnPropertyModified(): 属性变更时触发重新计算
// - CanAccept(): 检查计算是否完成
// - Shutdown(): 应用或取消结果

// 支持的参数化方法（通过 Settings 属性切换）：
// - UVAtlas: 高质量展开，适合复杂模型
// - XAtlas: 快速展开，适合简单模型
// - PatchBuilder: 基于多边形组的 Patch 展开
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UVEditorTools` | UV 编辑工具的运行时逻辑，提供工具属性类定义 |
| `MeshModelingToolset` | 交互式工具框架（InteractiveTool、ToolBuilder 等） |
| `GeometryProcessing` | UVAtlas、网格体参数化等几何处理算法 |