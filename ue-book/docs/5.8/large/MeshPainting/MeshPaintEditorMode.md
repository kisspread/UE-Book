# Mesh Painting

> System for painting data onto meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 网格绘制 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPaintEditorMode` (Editor), `MeshPaintingToolset` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-12-19 |
| 年龄标签 | 🏛️ 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshPainting) | |

## 用途

MeshPainting 是 Unreal Engine 编辑器中用于直接在网格体（如静态网格体、骨骼网格体）表面绘制各种数据的工具集。它解决的核心问题是：在游戏运行时或材质编辑之前，美术和关卡设计师需要直观地在网格表面“绘制”信息，以控制最终的视觉效果。

这个插件存在的意义在于提供一个集成化的编辑器模式，将原本可能需要在外部软件中处理或通过复杂材质节点实现的效果（如顶点颜色、蒙太奇权重混合、特定纹理通道的细节）直接内置于引擎编辑器中，极大地提升了迭代效率。

通过该工具，用户可以在编辑器视口内实时绘制，所见即所得，并且支持撤销/重做、复制/粘贴、在不同LOD和网格体实例间传播数据等专业功能。

## 使用场景

- 你需要为静态网格体绘制顶点颜色，用于后期处理材质或光照烘焙。
- 你需要为骨骼网格体绘制蒙太奇权重（例如，角色身体不同部位的物理模拟强度、肌肉隆起变形）。
- 你需要直接编辑网格体引用的纹理贴图的特定通道（如遮罩、粗糙度、金属度）来调整材质外观。
- 你需要将一个纹理的颜色信息采样并烘焙到网格体的顶点颜色上。
- 你在制作自定义资源（如地形材质混合、植被摆动强度）时，需要一种直观的方式来定义网格表面的数据分布。

## 蓝图用法

该插件的大部分功能通过编辑器模式和交互式工具（Interactive Tools）在视口中直接操作，蓝图公开的接口较少，主要是一些帮助函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportVertexColorsFromTexture` | 弹出选项窗口，将指定纹理的颜色采样并导入到网格组件的顶点颜色中。 | `UMeshPaintModeSubsystem` |
| `ImportVertexColorsToStaticMesh` | 将纹理颜色导入到静态网格体资产的顶点颜色中（根据选项）。 | `UMeshPaintModeSubsystem` |
| `ImportVertexColorsToStaticMeshComponent` | 将纹理颜色导入到静态网格体组件的实例顶点颜色中（根据选项）。 | `UMeshPaintModeSubsystem` |
| `PropagateVertexColors` | 将组件实例的顶点颜色传播到其源静态网格体资产。 | `UMeshPaintModeSubsystem` |
| `CopyVertexColors` | 复制一组静态网格体组件的实例顶点颜色数据。 | `UMeshPaintModeSubsystem` |
| `PasteVertexColors` | 将之前复制的顶点颜色数据粘贴到另一组静态网格体组件。 | `UMeshPaintModeSubsystem` |
| `ImportVertexColorsFromMeshPaintTexture` | 将网格体上“Mesh Paint Texture”通道的颜色导入为顶点颜色。 | `UMeshPaintModeSubsystem` |
| `ImportMeshPaintTextureFromVertexColors` | 将网格体的顶点颜色导入到其“Mesh Paint Texture”通道中。 | `UMeshPaintModeSubsystem` |

### 使用示例（蓝图描述）

由于该插件主要服务于编辑器模式，在蓝图编辑器中直接使用的场景有限。最常见的蓝图调用是利用 `UMeshPaintModeSubsystem` 的帮助函数。

**示例：在编辑器工具蓝图中导入顶点颜色**
1. 在编辑器工具蓝图中，获取 `UMeshPaintModeSubsystem` 子系统。
2. 调用 `ImportVertexColorsToStaticMesh` 节点，传入目标 `UStaticMesh` 资产、一个 `UImportVertexColorOptions` 对象（可预先设置好 UV 通道、LOD、颜色通道开关等）以及要采样的 `UTexture2D`。
3. 该节点执行后，会根据选项将纹理颜色烘焙到静态网格体的顶点颜色数据中。

## C++ 用法

### 头文件引入

```cpp
#include "MeshPaintMode.h"
#include "MeshPaintModeHelpers.h"
#include "MeshPaintModeCommands.h"
```

### 基本用法

```cpp
// 来自源码: MeshPaintEditorMode/Private/MeshPaintMode.h 和测试用例
// 1. 获取网格绘制编辑器模式实例
UMeshPaintMode* MeshPaintMode = UMeshPaintMode::GetMeshPaintMode();
if (MeshPaintMode)
{
    // 2. 获取当前选中的静态网格体组件
    TArray<UStaticMeshComponent*> SelectedComponents = MeshPaintMode->GetSelectedComponents<UStaticMeshComponent>();
    
    // 3. 检查当前选择是否适合绘制（例如，是否有可绘制的组件）
    FText WarningMessage;
    if (!MeshPaintMode->GetSelectionWarning(WarningMessage))
    {
        UE_LOG(LogTemp, Warning, TEXT("Selection not valid for painting: %s"), *WarningMessage.ToString());
    }
    
    // 4. 获取缓存的顶点数据大小
    uint32 VertexDataSize = MeshPaintMode->GetVertexDataSizeInBytes();
    UE_LOG(LogTemp, Log, TEXT("Vertex data size for selection: %d bytes"), VertexDataSize);
}
```

### 进阶用法

```cpp
// 结合命令系统与子系统功能
// 1. 注册网格绘制命令
FMeshPaintEditorModeCommands::Register();
FMeshPaintingToolActionCommands::RegisterAllToolActions();

// 2. 通过子系统执行操作
UMeshPaintModeSubsystem* Subsystem = GEditor->GetEditorSubsystem<UMeshPaintModeSubsystem>();
if (Subsystem && SomeStaticMeshComponent)
{
    // 从文件导入顶点颜色
    UImportVertexColorOptions* Options = NewObject<UImportVertexColorOptions>();
    Options->UVIndex = 0; // 使用第一个UV通道
    Options->LODIndex = 0;
    Options->bImportToInstance = true; // 导入到组件实例
    Options->bRed = true;
    Options->bGreen = true;
    Options->bBlue = true;
    Options->bAlpha = false; // 不导入Alpha通道
    
    UTexture2D* SourceTexture = LoadObject<UTexture2D>(nullptr, TEXT("/Game/Textures/MyColorPattern"));
    if (SourceTexture)
    {
        Subsystem->ImportVertexColorsToStaticMeshComponent(SomeStaticMeshComponent, Options, SourceTexture);
    }
}

// 3. 在工具中切换视口颜色视图模式
if (Subsystem && EditorViewportClient)
{
    Subsystem->SetViewportColorMode(EMeshPaintActiveMode::VertexColor, EMeshPaintDataColorViewMode::RGB, EditorViewportClient, nullptr);
    Subsystem->SetRealtimeViewport(EditorViewportClient, true); // 开启实时渲染以观察绘制效果
}
```

## Demo 示例

一个最小化的编辑器自动化测试示例，展示如何激活网格绘制模式并创建工具。

```cpp
// MyMeshPaintTest.h
#pragma once
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMyMeshPaintActivationTest,
    "Editor.MeshPainting.ActivateMode",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

// MyMeshPaintTest.cpp
#include "MyMeshPaintTest.h"
#include "MeshPaintMode.h"
#include "MeshPaintModeHelpers.h"
#include "EditorModeTools.h"
#include "Toolkits/ToolkitManager.h"

bool FMyMeshPaintActivationTest::RunTest(const FString& Parameters)
{
    // 确保在编辑器上下文中运行
    if (!GEditor || !GEditor->GetEditorSubsystem<UMeshPaintModeSubsystem>())
    {
        return false;
    }

    // 获取模式工具
    FEditorModeTools& ModeTools = GLevelEditorModeTools();

    // 激活网格绘制模式
    ModeTools.ActivateMode(FBuiltinEditorModes::EM_MeshPaint);

    // 验证模式已激活
    UMeshPaintMode* ActiveMode = Cast<UMeshPaintMode>(ModeTools.GetActiveMode(FBuiltinEditorModes::EM_MeshPaint).Get());
    TestTrue(TEXT("Mesh Paint Mode should be active"), ActiveMode != nullptr);

    if (ActiveMode)
    {
        // 获取工具管理器并检查默认工具是否已启动
        UInteractiveToolManager* ToolManager = ActiveMode->GetToolManager();
        TestNotNull(TEXT("Tool manager should be valid"), ToolManager);

        // 模拟完成测试后退出模式
        ModeTools.DeactivateMode(FBuiltinEditorModes::EM_MeshPaint);
    }

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 用于网格体几何数据处理，如顶点颜色传播和导入中的几何操作。 |
| `InterchangeEditor` | 用于资产交换和导入，特别是与纹理和网格体数据导入相关的功能。 |
| `MeshPaintingToolset` | 本插件的工具集模块，包含具体的绘制工具和交互逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2026-03-06 | `02b005a0` | make the mesh paint mode render geometry collections w/ the native render, so it does not show any p | 修改网格绘制模式，使其使用原生渲染器渲染几何体集合，避免显示某些伪影。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上次提交中错误的查找替换操作，这是第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的提交 CL51314860。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化后的委托从直接访问改为通过 Get 函数获取，以修复注册遗漏的问题。 |

### 维护评价

**维护状态：活跃维护中**

MeshPainting 是一个创建于2019年底的成熟插件，但其维护一直持续到2026年，最近几个月仍有功能性更新和底层优化。这表明 Epic Games 仍然将其视为编辑器工作流中的重要组成部分。

- **优势**：功能稳定，经过长期打磨，与引擎核心编辑器深度集成。持续更新以适配引擎新版本和修复问题。
- **注意事项**：作为编辑器工具，其使用场景明确限定在内容创作阶段，不会影响运行时性能。
- **推荐程度**：**强烈推荐**。对于任何需要在编辑器内进行网格表面数据绘制的工作（如美术、技术美术），这是官方提供的、功能最完善的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshPainting)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MeshPainting/Tests) (插件目录内可能有测试子目录)