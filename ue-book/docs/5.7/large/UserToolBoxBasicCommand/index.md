# UserToolBoxBasicCommand

> Basic set of command to populate a custom editor tab

| 属性 | 值 |
|---|---|
| 中文名 | 用户工具箱基本命令 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UserToolBoxBasicCommand` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UserToolBoxBasicCommand) | |

## 用途

本插件提供一系列预设好的编辑器命令，用于填充 `UserToolBoxCore` 插件创建的自定义编辑器标签页。它解决了在编辑器环境中快速执行常见操作（如隔离选中、改变视图模式、合并静态网格体、执行 Python 脚本等）的需求，无需手动编写重复脚本或点击多层菜单。通过组合这些基本命令，用户可以构建高效的工作流按钮，大幅提升编辑器操作效率。

## 使用场景

- **场景检查与隔离**：在大型关卡中快速隔离特定 Actor 组（如仅静态网格体），方便单独编辑。
- **批量操作**：对多个 Actor 统一执行操作（如翻转变换、推入材质、设置高精度）。
- **自定义工作流**：通过组合多个命令（复合命令、切换命令）创建一个点击即可执行一系列步骤的按钮。
- **脚本集成**：通过控制台命令或 Python 脚本快速执行复杂自动化任务。
- **层次清理**：清理从 Datasmith 导入后产生的多余层级结构，保留指定元数据。

## 蓝图用法

> **说明**：本插件大部分命令的 `Execute` 方法由 `UserToolBoxCore` 的 UI 按钮触发，不直接暴露为蓝图可调用节点。但您可以在 `UserToolBoxCore` 编辑器中通过蓝图类继承（Blueprintable）来定制命令行为，并利用 `BlueprintReadWrite` 属性调整参数。

### 核心节点

| 节点 / 属性 | 说明 | 所在类 |
|---|---|---|
| `UCompositeCommand::Execute` | 顺序执行子命令列表。 | `UCompositeCommand` |
| `UToggleCommand::Execute` | 循环执行子命令列表，每次点击切换到下一个子命令。 | `UToggleCommand` |
| `UConsoleVariable::Execute` | 执行一组控制台变量/命令。 | `UConsoleVariable` |
| `UEngineCommand::Execute` | 执行单个引擎命令字符串。 | `UEngineCommand` |
| `UExecutePythonScript::Execute` | 运行指定 Python 脚本文件。 | `UExecutePythonScript` |
| `UExecuteBindableAction::Execute` | 触发一个绑定动作（如菜单栏命令）。 | `UExecuteBindableAction` |
| `USelectActorByFilter::Execute` | 根据用户定义的过滤器（如过滤后代、父级等）重新选择 Actor。 | `USelectActorByFilter` |
| `UIsolateSelection::Execute` | 隐藏未选中的 Actor（仅保留选中对象）。 | `UIsolateSelection` |
| `UChangeViewMode::Execute` | 切换当前视口的显示模式（如光照、线框）。 | `UChangeViewMode` |
| `UAssignToLayer::Execute` | 将选中 Actor 分配到指定图层。 | `UAssignToLayer` |
| `UAssignToLevel::Execute` | 将选中 Actor 分配到当前关卡子关卡。 | `UAssignToLevel` |
| `UFillStaticMeshActor::Execute` | 用指定路径下的静态网格体填充空 StaticMeshActor。 | `UFillStaticMeshActor` |
| `UMirrorActorCommand::Execute` | 沿指定轴镜像选中 Actor。 | `UMirrorActorCommand` |
| `UMerge::Execute` | 合并选中的静态网格体 Actor。 | `UMerge` |
| `UFlipNormals::Execute` | 翻转选中静态网格体 Actor 的法线。 | `UFlipNormals` |
| `UPushComponentMaterialIntoMesh::Execute` | 将组件材质“推送”到关联的静态网格体中。 | `UPushComponentMaterialIntoMesh` |
| `UCleanHierarchy::Execute` | 清理 Datasmith 导入后 Actor 层次结构中的多余节点。 | `UCleanHierarchy` |
| `USelectActorBySize::Execute` | 根据尺寸阈值选择 Actor。 | `USelectActorBySize` |
| `USetHighPrecisionOnMesh::Execute` | 对选中的网格体设置高精度切线或 UV。 | `USetHighPrecisionOnMesh` |
| `UShowLayersCommand::Execute` | 显示/隐藏指定图层或隔离图层。 | `UShowLayersCommand` |
| `UZoomAll::Execute` | 执行“缩放全部”操作（在视口中框选所有 Actor）。 | `UZoomAll` |
| `UTabSpawner::Execute` | 强制打开指定编辑器标签页。 | `UTabSpawner` |

### 使用示例（蓝图描述）

在 `UserToolBoxCore` 编辑器中，您可以通过以下步骤创建一个“隔离并切换为线框模式”的复合命令：

1. 创建一个 `UCompositeCommand` 实例。
2. 在其 `Commands` 数组中添加两个子命令：
   - 添加 `UIsolateSelection`，设置 `bShouldOnlyAffectStaticMeshActor` 为 `true`（可选）。
   - 添加 `UChangeViewMode`，设置 `ViewMode` 为 `VMI_Wireframe`。
3. 将此复合命令绑定到 `UserToolBoxCore` 的按钮上即可。

## C++ 用法

### 头文件引入

```cpp
#include "UserToolBoxBasicCommand.h"
#include "UTBBaseCommand.h"            // 基类（来自 UserToolBoxCore）
#include "CompositeCommand.h"
#include "ToggleCommand.h"
#include "ConsoleVariable.h"
// 根据需要包含其他命令头文件
```

### 基本用法

通过 C++ 创建并执行一个复合命令（例如在编辑器模块启动时注册按钮）：

```cpp
// 示例：创建包含两个命令的复合命令
UCompositeCommand* MyCommand = NewObject<UCompositeCommand>();

// 第一个子命令：打印 Hello World 的控制台命令
UConsoleVariable* Cmd1 = NewObject<UConsoleVariable>();
Cmd1->ConsoleCommands.Add(TEXT("Hello World"));
MyCommand->Commands.Add(Cmd1);

// 第二个子命令：切换到线框视角
UChangeViewMode* Cmd2 = NewObject<UChangeViewMode>();
Cmd2->ViewMode = VMI_Wireframe;
MyCommand->Commands.Add(Cmd2);

// 执行（通常在按钮点击时触发）
MyCommand->Execute();
```

### 进阶用法

以下示例演示如何结合 `UExecuteBindableAction` 执行编辑器绑定动作（如打开内容浏览器）：

```cpp
#include "ExecuteBindableAction.h"

UExecuteBindableAction* OpenContentBrowser = NewObject<UExecuteBindableAction>();
OpenContentBrowser->CommandInfo.Context = TEXT("ContentBrowser");
OpenContentBrowser->CommandInfo.CommandName = TEXT("OpenContentBrowser");
OpenContentBrowser->Execute();
```

## Demo 示例

以下是一个完整的、可编译的编辑器模块示例，演示如何通过 C++ 创建一个复合命令并将其注册到 `UserToolBoxCore`（假设您已具备 UserToolBoxCore 的基本集成）。

**DemoCommand.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UTBBaseCommand.h"
#include "CompositeCommand.h"
#include "ConsoleVariable.h"
#include "ChangeViewMode.h"
#include "DemoCommand.generated.h"

/**
 * 一个预置的复合命令：打印信息后切换到线框模式
 */
UCLASS(Blueprintable)
class UDemoCompositeCommand : public UCompositeCommand
{
    GENERATED_BODY()
public:
    UDemoCompositeCommand()
    {
        Name = TEXT("Demo Command");
        Tooltip = TEXT("Prints a message and switches to wireframe mode.");
        Category = TEXT("Demo");
        
        // 在构造时自动添加子命令
        UConsoleVariable* Cmd1 = NewObject<UConsoleVariable>(this);
        Cmd1->ConsoleCommands.Add(TEXT("Hello from DemoCommand"));
        Commands.Add(Cmd1);
        
        UChangeViewMode* Cmd2 = NewObject<UChangeViewMode>(this);
        Cmd2->ViewMode = VMI_Wireframe;
        Commands.Add(Cmd2);
    }
};
```

**DemoCommand.cpp**
```cpp
#include "DemoCommand.h"
```

将此蓝图类添加到您的插件中，然后在 `UserToolBoxCore` 编辑器中将其实例化为一个按钮即可使用。

## 模块依赖

> **注意**：以下列表只包含该插件 **独特** 的依赖，已省略标准 Core/Engine/Slate 等常见模块。

| 模块 | 用途 |
|---|---|
| `UserToolBoxCore` | 提供 `UUTBBaseCommand` 基类以及 UI 框架，必须依赖。 |
| `EditorScriptingUtilities` | 供 `USelectActorByFilter` 等命令使用的编辑器脚本工具。 |
| `DatasmithContent` | 用于 `UCleanHierarchy` 命令中识别和处理 Datasmith 场景数据。 |
| `GeometryScripting` | 用于 `UFlipNormals`、`UMerge` 等涉及几何体操作的命令。 |

## 维护状态

### 近期更新

- 2025-03-05 `7ab43c2f` — 添加并处理 `UEditorInteractiveToolsContext` 类移动到 UnrealEd 后的弃用警告。
- 2025-02-04 `98d40fea` — 添加演员过滤器和新命令以支持汽车导入问题。
- 2025-01-23 `2c03c908` — 避免隔离演员时弄脏关卡。
- 2024-05-28 `15afa78d` — 添加测试以确保 `IMPLEMENT_MODULE` 宏中的模块名称与声明的名称匹配。
- 2023-02-14 `d1262967` — 修复所有非私有 UnrealEditor Win64 V3 路径问题。

### 维护评价

- **创建时间**：2023年2月，距今约2.5年，仍然是较新的插件。
- **活跃度**：最近半年内（2025年1月~3月）有多次功能性更新（新增过滤命令、修复隔离逻辑），维护活跃。
- **使用建议**：作为实验性插件，API 可能发生变动，但其提供了丰富的现成编辑器命令，适合搭配 `UserToolBoxCore` 快速搭建自定义工具栏。推荐用于节约编辑器重复劳动，但注意插件依赖较深（需要 UserToolBoxCore 等），不适合轻量级项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UserToolBoxBasicCommand)
- [官方文档](https://docs.unrealengine.com/)（该插件暂无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UserToolBoxBasicCommand/Tests)