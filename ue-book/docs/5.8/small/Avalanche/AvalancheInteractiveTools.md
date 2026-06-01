# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具，交互模式， Actor 工厂，场景管理模块等） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheViewport` (Runtime), `AvalancheMedia` (Runtime), `AvalancheSequencer` (Runtime) ... (共43个模块) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（内部代号 Motion Design）是一个用于虚拟制作和广播领域的**动态图形设计与合成系统**。它并非一个单一功能插件，而是一整套工具集和运行时框架，旨在解决以下问题：

1.  **快速视口内创建与编辑**：提供了一套交互式工具（Interactive Tools），允许用户在视口（Viewport）中直接点击、拖拽来创建和编辑几何体、文本、形状、样条等 Actor，大幅提升场景搭建效率。
2.  **程序化与效果器系统**：包含克隆器（Cloner）和效果器（Effector）系统，用于创建程序化动画和效果，如粒子、实例化网格的动态生成与控制。
3.  **媒体与序列集成**：深度集成了媒体播放、合成（Compositing）和 Sequencer 时间线，便于将动态图形元素与实时视频源、预制动画同步。
4.  **场景管理与控制**：提供了场景大纲（Outliner）、场景 rig、远程控制、节目单（Rundown）等功能，适用于现场直播、虚拟制作等需要复杂场景管理和远程控制的工作流。

其存在是为了让艺术家和设计师能够在一个一体化的环境中，从概念设计到最终播出，高效地完成动态图形内容的创作。

## 使用场景

-   **你在为一场虚拟演唱会或电视节目制作实时播放的动态图形**：使用 Motion Design 在视口中快速搭建舞台元素、灯光和文字动画，并通过媒体模块接入视频源，利用节目单功能进行播放控制。
-   **你需要创建复杂的程序化动画效果，如万千碎片飞散或粒子汇聚成字**：使用 ClonerEffector 系统，并结合属性动画（PropertyAnimator）实现动态控制。
-   **你需要快速原型化一个带有交互式元素的 3D 场景**：使用 AvalancheInteractiveTools 模块中的工具，直接在视口中绘制样条、放置预设网格、创建简单几何体。
-   **你需要将动态图形与外部设备（如DMX灯光、MIDI控制器）同步**：利用 Remote Control 模块进行参数映射和实时控制。

## 蓝图用法

由于插件规模庞大且高度模块化，其核心蓝图节点分散在各个子模块中。以下基于 `AvalancheInteractiveTools` 模块的核心接口，列出关键蓝图可用功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `On Tool Activation` | 当一个交互式工具被激活时触发的委托，可绑定蓝图事件进行响应。 | `IAvalancheInteractiveToolsModule` |
| `On Tool Deactivation` | 当一个交互式工具被停用时触发的委托。 | `IAvalancheInteractiveToolsModule` |
| `Has Active Tool` | 检查当前是否有正在活动的交互式工具。 | `IAvalancheInteractiveToolsModule` |

### 使用示例（蓝图描述）

1.  **监听工具状态**：在任意 Blueprint Actor 中，通过 `IAvalancheInteractiveToolsModule::Get()` 获取模块实例，并绑定 `On Tool Activation` 和 `On Tool Deactivation` 事件。当用户激活“放置空 Actor”或“绘制样条”等工具时，你的蓝图可以收到通知并执行自定义逻辑（例如更新UI、记录日志）。
2.  **自定义工具行为**：要创建一个完全自定义的交互式工具（例如，点击视口生成一个特定逻辑的Actor），需要：
    a. 创建一个继承自 `UAvaInteractiveToolsToolBase` 的 C++ 类，并重写 `OnBegin`, `OnClickPress`, `OnDragStart` 等方法。
    b. 创建一个对应的 `UInteractiveToolBuilder` 子类。
    c. 在模块启动时，通过 `IAvalancheInteractiveToolsModule::RegisterTool` 将你的工具注册到指定分类下。
    (注：这是一个纯C++流程，蓝图主要用于监听和响应工具事件，而非创建新工具。)

## C++ 用法

核心用法集中在 `AvalancheInteractiveTools` 模块的接口上。

### 头文件引入

```cpp
#include "IAvalancheInteractiveToolsModule.h"
```

### 基本用法

**注册一个自定义交互式工具（分类与工具注册）**

来自模块的公共接口，展示如何注册工具分类和工具。

```cpp
// 来自：Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheInteractiveTools/Public/IAvalancheInteractiveToolsModule.h
// 1. 获取模块引用
IAvalancheInteractiveToolsModule& AITModule = IAvalancheInteractiveToolsModule::Get();

// 2. 注册一个新的工具分类（通常在模块Startup时调用一次）
FName MyCategoryName = TEXT("MyCustomTools");
TSharedPtr<FUICommandInfo> MyCategoryCommand = ...; // 创建一个UI命令信息
int32 SortPriority = 10; // 在放置模式面板中的排序优先级
AITModule.RegisterCategory(MyCategoryName, MyCategoryCommand, SortPriority);

// 3. 准备工具参数并注册
// 创建一个Actor工具的参数（假设要放置一个自定义的AStaticMeshActor）
FAvaInteractiveToolsToolParameters ToolParams;
ToolParams.UICommand = MyPlaceCommand; // 关联的UI命令
ToolParams.ToolIdentifier = TEXT("PlaceMyMesh"); // 工具唯一标识符
ToolParams.Priority = 0;
ToolParams.CreateBuilder = [](UEdMode* InEdMode) -> UInteractiveToolBuilder* {
    // 这里返回你的工具Builder实例，通常是UAvaInteractiveToolsActorToolBuilder等
    return UAvaInteractiveToolsActorToolBuilder::CreateActorToolBuilder(
        InEdMode, MyCategoryName, MyPlaceCommand, TEXT("PlaceMyMesh"), 0,
        AMyCustomActor::StaticClass() // 要生成的Actor类
    );
};
// 注册工具到指定分类
AITModule.RegisterTool(MyCategoryName, MoveTemp(ToolParams));
```

### 进阶用法

**创建一个自定义的点击-拖拽交互工具**

此示例展示如何通过继承基类来创建一个在视口中点击放置，拖拽调整大小的自定义区域生成器。

```cpp
// 头文件（简化示例）
// 来自：Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheInteractiveTools/Public/Tools/AvaInteractiveToolsToolBase.h
UCLASS()
class UMyAreaSpawnTool : public UAvaInteractiveToolsToolBase
{
    GENERATED_BODY()
public:
    // 重写工具激活时的初始化
    virtual void OnActivate() override;
    // 重写点击开始
    virtual void OnClickPress(const FInputDeviceRay& InPressPos) override;
    // 重写拖拽更新
    virtual void OnClickDrag(const FInputDeviceRay& InDragPos) override;
    // 重写点击释放，完成生成
    virtual void OnClickRelease(const FInputDeviceRay& InReleasePos, bool bInIsDragOperation) override;
    // 重写HUD绘制，用于显示生成框
    virtual void DrawHUD(FCanvas* InCanvas, IToolsContextRenderAPI* InRenderAPI) override;

private:
    FVector StartWorldPosition;
    FVector CurrentWorldPosition;
    bool bIsDragging = false;
};

// .cpp文件（逻辑片段）
void UMyAreaSpawnTool::OnClickPress(const FInputDeviceRay& InPressPos)
{
    // 将视口位置转换为世界位置
    UWorld* World = nullptr;
    FVector Position;
    FRotator Rotation;
    if (ViewportPositionToWorldPositionAndOrientation(EAvaViewportStatus::Hovered, InPressPos.ScreenPosition, World, Position, Rotation))
    {
        StartWorldPosition = Position;
        bIsDragging = true;
    }
}

void UMyAreaSpawnTool::OnClickDrag(const FInputDeviceRay& InDragPos)
{
    if (bIsDragging)
    {
        // 更新当前拖拽位置
        UWorld* World = nullptr;
        FVector Position;
        FRotator Rotation;
        if (ViewportPositionToWorldPositionAndOrientation(EAvaViewportStatus::Hovered, InDragPos.ScreenPosition, World, Position, Rotation))
        {
            CurrentWorldPosition = Position;
            // 更新预览Actor或绘制
        }
    }
}
```

## Demo 示例

由于 Motion Design 是一个庞大的系统，包含数十个模块和数百个类，无法在单个文档中提供完整的编译示例。其最佳“示例”是查看插件内置的各种工具实现，例如：

-   **基本的 Actor 放置工具**：`UAvaInteractiveToolsActorToolNull`（空Actor）、`UAvaInteractiveToolsActorToolSpline`（样条）。
-   **带有几何形状的 Actor 工具**：`UAvaInteractiveToolsActorToolBase` 的子类。
-   **使用静态网格的 Actor 工具**：`UAvaInteractiveToolsStaticMeshActorTool`。

这些工具的代码位于 `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheInteractiveTools/Private/Tools/` 目录下，是学习如何基于该框架创建自定义交互工具的最佳起点。

## 模块依赖

从插件的描述和模块结构来看，`Avalanche` 依赖于大量 Unreal Engine 和 Epic 其他插件的模块。以下是其独特的、不常见的依赖：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 提供高级重命名功能，用于批量管理资产和Actor。 |
| `CustomDetailsView` | 用于构建高度自定义的细节面板（Details Panel）UI。 |
| `DynamicMaterial` | 动态材质创建与编辑框架。 |
| `GeometryCache` | 几何体缓存，用于播放烘焙的顶点动画。 |
| `GeometryScripting` | 通过脚本进行程序化几何体生成与操作。 |
| `MediaCompositing` | 媒体合成，用于将实时视频源与场景元素混合。 |
| `MediaIOFramework` | 媒体输入输出框架，处理硬件采集卡等设备。 |
| `MeshModelingToolsetExp` | 实验性网格建模工具集，提供交互式建模能力。 |
| `RemoteControl` | 远程控制协议支持，用于外部设备（DMX, MIDI）控制引擎参数。 |
| `SVGImporter` | SVG文件导入器，用于导入矢量图形。 |
| `Text3D` | 3D文本生成组件。 |
| `ActorModifierCore` | Actor修改器系统核心框架。 |
| `Sequencer` | （通过`AvalanchePropertyAnimator`依赖）用于基于时间线的属性动画。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的标签页（场景设置、大纲视图）移动到关卡编辑器中的独立分组，优化了UI布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在使用节目单（Rundown）页面设置时，增加了MRQ（Movie Render Queue）的分析数据收集功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏增加了页面加载选项（全部、下一个、已选），并添加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了一个项目设置，用于强制禁用Text3D和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构了视口相关代码，通过在客户端关联或断开关联时进行通知来减少冗余代码。 |

### 维护评价

-   **创建时间**：2025年5月，是一个相对较新的插件。
-   **维护活跃度**：**非常活跃**。截至2026年5月，仍有持续的功能性更新（如MRQ分析、UI重构、新增设置项）和优化提交。这表明 Epic Games 的虚拟制作团队正在积极开发和维护此工具。
-   **状态**：正式插件。已从 `Experimental` 目录迁移至 `VirtualProduction`，表明其已达到生产可用状态。
-   **推荐使用**：✅ **强烈推荐**。对于虚拟制片、广播和动态图形领域的用户，这是 Unreal Engine 中核心且功能强大的官方工具集。它提供了从设计到播出的完整工作流，社区支持和文档也在不断完善中。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/) (待补充，可参考UE官方文档站)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) (部分功能测试位于此目录)