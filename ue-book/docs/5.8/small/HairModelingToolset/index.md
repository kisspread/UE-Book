# Hair Modeling Toolset

> Adds a set of tools for Groom/Hair Modeling to Modeling Tools Mode

| 属性 | 值 |
|---|---|
| 中文名 | 毛发建模工具集 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（建模工具） |
| 模块 | `HairModelingToolset` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairModelingToolset) | |

## 用途

此插件为 Groom（毛发）资产提供了一套专门的建模工具，主要解决以下问题：
- **Groom到网格转换**：将复杂的Groom/毛发资产转换为传统网格，以便进行进一步编辑、优化或用于不支持Groom的引擎。转换过程包括体素化、形态学操作、裁剪、平滑和简化。
- **LOD网格生成**：为毛发网格自动生成多个细节层次（LOD）的简化版本，用于性能优化。
- **毛发卡片编辑**：直接编辑Groom中的"卡片"（Card）元素，允许选择、删除等操作，用于精细调整毛发外观。

该插件通过建模模式扩展API（Modeling Mode Extension API）将这些工具集成到UE的建模模式中，作为实验性功能提供。

## 使用场景

- 你需要将Groom资产转换为传统网格（Static Mesh）进行烘焙或用于不支持Groom的平台 → 使用 GroomToMeshTool。
- 你需要为毛发资产创建多个LOD版本以优化渲染性能 → 使用 GenerateLODMeshesTool。
- 你需要直接编辑Groom资产中的卡片结构（如删除某些卡片） → 使用 GroomCardsEditorTool。
- 你正在使用建模模式并希望添加专门的毛发建模工具 → 启用此插件后，工具将出现在建模模式的"毛发工具"部分。

## 蓝图用法

此插件的工具主要通过编辑器UI（建模模式面板）使用，不提供传统意义上的蓝图函数。所有工具都是交互式的，在特定上下文中激活。

### 核心工具

| 工具 | 说明 | 所在类 |
|---|---|---|
| Groom To Mesh | 将选定的 Groom Actor 转换为带有可选 UV 的网格 | `UGroomToMeshTool` |
| Generate LOD Meshes | 为选定的毛发网格资产生成多个 LOD 级别 | `UGenerateLODMeshesTool` |
| Groom Cards Editor | 编辑 Groom 资产中的卡片（选择、删除等） | `UGroomCardsEditorTool` |

### 使用示例（工具激活）

1.  启用插件：在插件管理器中找到 "Hair Modeling Toolset"，启用它。
2.  打开建模模式：在视口工具栏中切换到建模模式。
3.  找到工具：在建模模式的工具栏或面板中，找到 "Hair Tools" 部分（名称由模块注册）。
4.  选择对象：
    -   对于 "Groom To Mesh"：在场景中选择一个 `AGroomActor`。
    -   对于 "Generate LOD Meshes"：在内容浏览器中选择一个网格资产（预期用于毛发）。
    -   对于 "Groom Cards Editor"：在场景中选择一个包含卡片数据的 `AGroomActor`。
5.  激活工具并调整属性：根据工具的属性面板调整参数（如体素化密度、LOD百分比等）。
6.  接受或取消：完成编辑后，点击工具栏中的对勾（接受）或叉号（取消）。

## C++ 用法

这些工具是为编辑器使用设计的，通过编辑器工具框架（Interactive Tools Framework）构建。通常，开发者无需直接调用它们的C++接口，但可以通过研究其源码来理解或扩展类似工具。

### 头文件引入

```cpp
#include "HairModelingToolset.h" // 模块主头文件（通常）
// 工具类头文件
#include "GroomToMeshTool.h"
#include "GenerateLODMeshesTool.h"
#include "GroomCardsEditorTool.h"
```

### 基本用法（创建工具实例）

工具实例通常由其对应的 `ToolBuilder` 创建，并在编辑器工具管理器（`UInteractiveToolManager`）的控制下运行。以下是一个概念性示例，展示如何通过代码构建和激活一个工具（实际中由建模模式框架处理）。

```cpp
// 概念示例：手动构建 GroomToMeshTool（通常由建模模式框架自动处理）
#include "InteractiveToolManager.h"
#include "GroomToMeshTool.h"

void SpawnGroomToMeshTool(UWorld* World, AGroomActor* TargetGroom)
{
    // 获取当前的工具管理器（需要在编辑器上下文中）
    UInteractiveToolManager* ToolManager = /* ... */;
    if (!ToolManager) return;

    // 创建工具构建器
    UGroomToMeshToolBuilder* Builder = NewObject<UGroomToMeshToolBuilder>();

    // 检查是否能构建工具（需要 GroomActor 处于可编辑状态）
    FToolBuilderState SceneState;
    // ... 填充 SceneState ...
    if (Builder->CanBuildTool(SceneState))
    {
        // 构建工具
        UGroomToMeshTool* Tool = Cast<UGroomToMeshTool>(Builder->BuildTool(SceneState));
        if (Tool)
        {
            // 设置目标
            Tool->SetWorld(World);
            Tool->SetSelection(TargetGroom);

            // 激活工具（通过工具管理器）
            ToolManager->RegisterTool(Tool);
            ToolManager->ActivateTool(Tool);
        }
    }
}
```

*来源：工具激活逻辑参考自建模模式扩展API，具体实现见 `HairModelingToolsetModule.cpp`。*

### 进阶用法（理解工具属性结构）

每个工具都有一组 `UInteractiveToolPropertySet` 子类来暴露其可编辑参数。了解这些属性可以帮助你理解工具的功能。

```cpp
// 示例：GroomToMeshTool 的主要属性（来自 GroomToMeshToolProperties）
// 在源码中查看：GroomToMeshTool.h

// 体素化相关
int32 VoxelCount = 64;      // 体素网格分辨率
float BlendPower = 1.0;     // 混合强度
float RadiusScale = 100.0;  // 半径缩放

// 形态学操作
bool bApplyMorphology = true;
float ClosingDist = 2.0;    // 闭合距离
float OpeningDist = 0.25;   // 开启距离

// 裁剪
bool bClipToHead = true;
AStaticMeshActor* ClipMeshActor; // 用于裁剪的网格Actor

// 平滑
bool bSmooth = true;
float Smoothness = 0.15f;
float VolumeCorrection = -0.25f;

// 简化
bool bSimplify = false;
int VertexCount = 500;      // 目标顶点数

// UV 生成模式
EGroomToMeshUVMode UVMode = EGroomToMeshUVMode::MinimalConformal;
```

## Demo 示例

由于这些工具是编辑器专用的交互式工具，无法在运行时（Runtime）代码中创建一个独立的演示。演示的正确方式是在UE编辑器中操作。

**最小步骤演示：**
1.  创建一个包含Groom Actor的新关卡。
2.  启用 HairModelingToolset 插件（如果未启用）。
3.  进入建模模式。
4.  选择 Groom Actor，然后找到并点击 "Groom To Mesh" 工具。
5.  在属性面板中调整参数（如将 VoxelCount 改为 128），观察预览。
6.  点击对勾接受，生成的网格将作为一个新资产出现在内容浏览器中。

## 模块依赖

此插件的 `Build.cs` 文件中列出了一些独特的依赖模块，以便使用其提供的建模工具和几何处理功能。

| 模块 | 用途 |
|---|---|
| `MeshModelingToolset` | 提供基础建模工具框架、交互式工具、预览几何体等 |
| `GeometryProcessing` | 提供网格操作（简化、体素化、UV生成等） |
| `ModelingComponents` | 提供建模模式组件（如预览网格、选择机制等） |
| `Groom` | 提供 Groom 资产和 Actor 的核心类定义 |
| `HairStrandsCore` | 提供毛发发丝核心数据结构（用于访问Groom数据） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数产生的警告代码。 |
| 2026-04-02 | `d1c0f5e7` | TLazyObjectPtr Deprecation pt 2.: | 继续替换已废弃的 TLazyObjectPtr 指针类型。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复无法到达的代码错误。 |
| 2025-06-03 | `e5e94e83` | Add support for custom/additional UV channels for hair cards/hair meshes. | 为毛发卡片/网格添加对自定义/额外UV通道的支持。 |
| 2024-12-20 | `d0cf4301` | ModelingTools: Promote experimental modeling tools to beta. | 建模工具：将实验性建模工具提升为 Beta 版。 |

### 维护评价

- **年龄**：插件创建于2021年，已有约4年历史，属于较新的工具。
- **更新频率**：近期（2025-2026年）有持续的维护更新，主要集中在**代码质量改进**（修复警告、错误、废弃类型替换）和**功能增强**（添加UV通道支持）。
- **状态**：虽然最初标记为实验性（`IsExperimentalVersion=true`），但2024年12月的commit表明相关工具（可能是依赖的建模工具集）已提升至Beta版，这暗示此插件可能也逐渐走向稳定。
- **已知问题/限制**：文档中未明确提及，但作为实验性工具，可能存在与特定Groom资产或复杂场景的兼容性问题。工具性能（如体素化）可能对复杂毛发资产有较高要求。
- **推荐**：**推荐在需要上述特定功能（Groom转网格、LOD生成、卡片编辑）的编辑器工作流中使用**。由于是实验性功能，建议在生产环境备份资产后使用。它解决了Groom资产与传统网格工作流之间的重要转换需求，维护状态良好。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairModelingToolset)
- 官方文档：无（.uplugin 中 DocsURL 为空）