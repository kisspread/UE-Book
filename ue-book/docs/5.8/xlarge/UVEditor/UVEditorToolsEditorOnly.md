# UVEditor

> Asset editor for modifying the UV mapping of a mesh

| 属性 | 值 |
|---|---|
| 中文名 | UV编辑器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor) | |

## 用途

UVEditor 是一个为 Unreal Engine 提供的专用资产编辑器，其核心目的是为网格体（Mesh）提供一个强大、全面的 UV 映射编辑环境。它超越了引擎内置的 StaticMesh 编辑器基础功能，提供了一整套交互式工具，用于在编辑器内直观地布局、编辑、展开和优化模型的 UV 坐标。插件通过提供诸如 UV 变换、接缝创建、自动展开和图表打包等功能，旨在解决复杂模型（如角色、硬表面道具）的 UV 制作和优化问题，是美术师在引擎内进行精细 UV 调整的关键工具。

## 使用场景

*   **3D 美术师需要手动调整复杂模型的 UV**：对于角色、有机体或结构复杂的模型，美术师需要直观地移动、旋转、缩放 UV 岛，并手动设置接缝线，以优化贴图空间利用和减少拉伸。此时应使用 **UVEditor**。
*   **需要自动展开和优化 UV 的工作流**：当处理具有大量多边形或简单几何体的模型，希望快速获得合理的 UV 布局时，可以使用 UVEditor 内置的 **ParameterizeMeshTool**（自动展开工具），选择 UVAtlas、XAtlas 或 PatchBuilder 等不同算法进行自动 UV 展开和图表打包。
*   **需要精确控制 UV 图表的对齐、分布和对称**：在整理 UV 时，美术师经常需要将 UV 图表对齐到边缘、均匀分布间距或创建对称的 UV 布局，UVEditor 提供了专门的 **Transform**、**Align** 和 **Distribute** 工具来满足这些需求。

## 蓝图用法

UVEditor 主要是一个编辑器工具，其大部分功能通过编辑器 UI 和交互式工具访问。以下是其模块中暴露给蓝图的核心构建类，通常用于创建和初始化工具实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UUVEditorParameterizeMeshToolBuilder` | 用于构建自动 UV 展开工具的工厂类。 | `UUVEditorParameterizeMeshToolBuilder` |
| `UUVEditorToolMeshInput` | 代表在 UV 编辑工具中操作的网格输入数据。 | `UUVEditorToolMeshInput` |

### 使用示例（蓝图描述）

由于 UVEditor 主要服务于编辑器操作，直接在蓝图中创建独立工具流的场景较少。典型流程是在 UVEditor 资产编辑器内部，由工具模式（如 `UUVEditorUVTransformToolMode`）创建相应的工具构建器实例，并将当前编辑器的 `UUVEditorToolMeshInput` 目标列表传递给构建器，最终调用 `BuildTool` 来实例化具体的交互式工具（如 `UUVEditorParameterizeMeshTool`）。用户通过细节面板与工具交互。

## C++ 用法

本插件模块 `UVEditorToolsEditorOnly` 主要包含工具的属性面板定制和特定的编辑器专用工具。使用通常发生在扩展 UVEditor 或创建自定义 UV 工具时。

### 头文件引入

```cpp
// 引入自动展开工具
#include "UVEditorParameterizeMeshTool.h"

// 引入属性面板定制类（用于扩展工具UI）
#include "DetailsCustomizations/UVTransformToolCustomizations.h"
#include "DetailsCustomizations/UVEditorSeamToolCustomizations.h"
```

### 基本用法

以下示例展示了如何在自定义工具或编辑器扩展中使用 `UUVEditorParameterizeMeshTool`。代码逻辑参考了 `UUVEditorParameterizeMeshToolBuilder` 的实现。

```cpp
// 假设我们已经获得了网格输入目标，例如从 UVEditor 中获取
TArray<TObjectPtr<UUVEditorToolMeshInput>> EditorTargets = GetEditorTargets();

// 1. 创建工具构建器实例
UUVEditorParameterizeMeshToolBuilder* Builder = NewObject<UUVEditorParameterizeMeshToolBuilder>();

// 2. 设置构建器的网格目标
Builder->Targets = &EditorTargets;

// 3. 检查是否可以构建工具（需要目标有效）
FToolBuilderState SceneState; // 此处为示例，通常从上下文获取
if (Builder->CanBuildTool(SceneState))
{
    // 4. 构建工具实例
    UInteractiveTool* Tool = Builder->BuildTool(SceneState);
    UUVEditorParameterizeMeshTool* ParameterizeTool = Cast<UUVEditorParameterizeMeshTool>(Tool);

    if (ParameterizeTool)
    {
        // 5. 设置工具的目标并启动
        ParameterizeTool->SetTargets(EditorTargets);
        ParameterizeTool->Setup(); // 或通过工具管理框架启动

        // 工具现在处于活动状态，等待用户操作并调用 Shutdown
    }
}
```
*来源文件: `Public/UVEditorParameterizeMeshTool.h`*

### 进阶用法

`UVEditorToolsEditorOnly` 模块的一个重要功能是提供 **Details Panel Customization**（细节面板自定义）。这允许开发者扩展或修改现有 UV 编辑工具在属性面板中的显示方式和交互逻辑。

```cpp
// 1. 在模块启动时（StartupModule）注册属性面板自定义
void FUVEditorToolsEditorOnlyModule::StartupModule()
{
    // 注册 UUVEditorUVTransformProperties 的细节自定义
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    PropertyModule.RegisterCustomClassLayout(
        UUVEditorUVTransformProperties::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(&FUVEditorUVTransformToolDetails::MakeInstance)
    );
    // ... 注册其他自定义，如 Align, Distribute, Seam 工具的
    PropertyModule.NotifyCustomizationModuleChanged();
}

// 2. 自定义类 FUVEditorUVTransformToolDetails 可以完全控制属性面板
void FUVEditorUVTransformToolDetails::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
    // 获取工具属性对象
    TArray<TWeakObjectPtr<UObject>> Objects;
    DetailBuilder.GetObjectsBeingCustomized(Objects);
    // ... 添加自定义按钮、组合属性、验证逻辑等
    // 例如，构建快速移动/旋转的菜单按钮
    BuildQuickTranslateMenu(DetailBuilder);
}
```
*来源文件: `Public/DetailsCustomizations/UVTransformToolCustomizations.h`, `Public/UVEditorToolsEditorOnlyModule.h`*

## Demo 示例

以下是一个最小示例，演示如何创建一个继承自 `UInteractiveTool` 的简单 UV 编辑器工具骨架，并利用 `UUVEditorToolMeshInput`。注意，完整的 UV 编辑器工具需要集成到 `UInteractiveToolManager` 和 UVEditor 的特定模式中才能工作。

**MySimpleUVTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InteractiveTool.h"
#include "UVEditorToolMeshInput.h" // 来自 UVEditorTools 模块

#include "MySimpleUVTool.generated.h"

UCLASS()
class UMySimpleUVToolProperties : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "MyTool")
    bool bFlipUVs = false;
};

UCLASS()
class UMySimpleUVTool : public UInteractiveTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;
    virtual void OnTick(float DeltaTime) override;

    void SetTargets(const TArray<TObjectPtr<UUVEditorToolMeshInput>>& InTargets) { Targets = InTargets; }

protected:
    UPROPERTY()
    TArray<TObjectPtr<UUVEditorToolMeshInput>> Targets;

    UPROPERTY()
    TObjectPtr<UMySimpleUVToolProperties> Properties;
};
```

**MySimpleUVTool.cpp**
```cpp
#include "MySimpleUVTool.h"

void UMySimpleUVTool::Setup()
{
    UInteractiveTool::Setup();

    // 创建属性对象
    Properties = NewObject<UMySimpleUVToolProperties>(this);
    AddToolPropertySource(Properties);

    // 对每个目标网格体执行一些初始设置...
    for (UUVEditorToolMeshInput* Target : Targets)
    {
        if (Target && Target->GetMesh())
        {
            // 此处可以获取网格体数据，准备进行 UV 操作
            // UE_LOG(LogTemp, Log, TEXT("Tool setup for target with %d triangles."), Target->GetMesh()->TriangleCount());
        }
    }
}

void UMySimpleUVTool::Shutdown(EToolShutdownType ShutdownType)
{
    // 根据关闭类型决定是应用还是丢弃更改
    if (ShutdownType == EToolShutdownType::Accept)
    {
        // 应用最终的 UV 更改...
    }
    Super::Shutdown(ShutdownType);
}

void UMySimpleUVTool::OnTick(float DeltaTime)
{
    // 工具可以在此处理持续输入或动画
    if (Properties->bFlipUVs)
    {
        // 执行 UV 翻转逻辑...
    }
}
```

## 模块依赖

本插件依赖于其他几个关键插件，以提供几何处理、网格体建模和工具集基础设施。

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供底层几何算法，如网格体参数化、UV 展开和打包的核心计算能力。 |
| `ModelingComponents` | 提供基础建模工具框架、交互式工具管理器和目标网格体管理组件。 |
| `MeshModelingToolset` | 提供一系列标准的网格体建模工具，UVEditor 中的部分操作可能复用其组件或逻辑。 |
| `MeshModelingToolsetExp` | `MeshModelingToolset` 的实验性扩展工具集。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，将双精度常量截断为单精度浮点数产生的编译警告。 |
| 2026-04-24 | `0213bc37` | [ITF] Call `UInputRouter::ForceTerminateSource()` from within `UInputRouter::DeregisterSource()` pri | [输入工具框架] 在注销输入源时，优先调用`ForceTerminateSource()`以确保状态清理。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从 `UE_LOG` 迁移至新的 `UE_LOGF` 格式化宏。 |
| 2026-03-10 | `0b781d0c` | Add/RemoveOverlayWidget: | 改进了向编辑器界面添加或移除覆盖层部件的接口或逻辑。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 开始了新的材质转换器相关工作。 |

### 维护评价

UVEditor 是一个**处于活跃维护中**的插件。
*   **创建时间**：约 3 年前（2023年），属于相对较新的功能。
*   **更新频率**：近期（2026年）的提交记录显示持续有维护性更新和功能改进，包括输入系统、代码现代化和底层重构。
*   **状态**：插件在 `.uplugin` 中标记为 `IsBetaVersion: true`，表明它仍在积极开发和完善中，功能可能发生变化。
*   **推荐**：**推荐使用**。作为官方提供的专用 UV 编辑器，它功能强大且持续更新，是进行引擎内 UV 工作的首选方案。需要注意其 Beta 状态意味着未来版本可能有接口变动。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor)
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor/Source/UVEditorToolsEditorOnly/Private/Tests) (注：测试代码位于源码目录内)