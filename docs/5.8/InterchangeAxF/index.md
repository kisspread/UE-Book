# Interchange AxF

> Imports AxF2UE files from X-Rite Pantora as Substrate materials via the Interchange framework.

| 属性 | 值 |
|---|---|
| 分类 | 未分类 |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产） |
| 模块 | `InterchangeAxF` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InterchangeAxF) | |

## 用途

此插件是 **Interchange 框架**的一个扩展，专门用于导入 **X-Rite Pantora** 软件生成的 **AxF (Appearance Exchange Format)** 材质文件（`.axf`）。AxF 是一种行业标准格式，用于精确捕获和交换物理材质的外观属性，常用于产品可视化、汽车渲染等领域。

该插件的核心功能是将 AxF 文件中包含的复杂材质数据（如各向异性、清漆层、薄片、高度图等）解析并转换为 Unreal Engine 的 **Substrate 材质系统**（一种先进的材质模型）。它通过实现自定义的 `Translator` 和 `Pipeline`，无缝集成到 UE 的资产导入流程中，使用户能够直接将 AxF 文件拖入编辑器，自动生成对应的材质资产和纹理。

## 使用场景

- **产品可视化与工业设计**：当你需要导入由 X-Rite Pantora 创建的、具有精确物理外观的材质（如汽车漆面、塑料、织物）时。
- **跨软件材质工作流**：当你的材质资产来源于支持 AxF 标准的第三方软件（如 VRED、KeyShot），并需要在 UE 中保持视觉一致性时。
- **需要高级材质特性**：当你的项目需要使用 Substrate 材质系统，并且需要利用 AxF 中定义的复杂材质层（如 ClearCoat、Flakes、Sheen）时。

## 蓝图用法

此插件主要通过 Interchange 框架的配置界面（导入对话框中的管线设置）进行控制，而非直接通过蓝图节点调用。其核心逻辑封装在 `UAxFInterchangePipeline` 和 `UAxFTranslator` 中。

### 核心配置属性

在导入 AxF 文件时，可以在 Interchange 导入对话框的管线设置中找到以下选项：

| 属性 | 说明 | 所在类 |
|---|---|---|
| `PipelineDisplayName` | 管线在UI中的显示名称。 | `UAxFInterchangePipeline` |
| `ReimportStrategy` | 设置重新导入策略（例如，是否应用属性）。 | `UAxFInterchangePipeline` |
| `bUseTriplanarMappingByDefault` | 是否默认为生成的纹理使用三平面映射。 | `UAxFInterchangePipeline` |

### 使用示例（蓝图描述）

1.  将 `.axf` 文件从文件浏览器拖拽到 UE 内容浏览器中。
2.  在弹出的 **Interchange 导入** 对话框中，确保 **管线** 下拉菜单选择了 **AxF Interchange Pipeline**。
3.  在下方的属性面板中，根据需要调整 `ReimportStrategy` 和 `bUseTriplanarMappingByDefault` 等设置。
4.  点击 **导入**，插件将自动处理文件，生成材质和纹理资产。

## C++ 用法

此插件主要作为 Interchange 框架的扩展运行，开发者通常不需要直接调用其 C++ API。其核心价值在于实现了 `UInterchangeTranslatorBase` 和 `UInterchangePipelineBase` 的接口。

### 头文件引入

```cpp
#include "AxFTranslator.h"
#include "AxFInterchangePipeline.h"
#include "AxFMaterialObjectNode.h"
```

### 基本用法（理解内部工作流）

插件的核心工作流如下（供理解，非直接调用）：

1.  **翻译阶段 (`UAxFTranslator::Translate`)**:
    - 当 Interchange 框架检测到 `.axf` 文件时，会调用 `UAxFTranslator`。
    - `Translate` 函数解析 AxF 文件，创建 `UAxFMaterialObjectNode` 节点，并将材质数据（颜色值、使用的特性列表）存储在 `PayloadData` 中。
    - 同时，它会为文件中的纹理创建对应的 `UInterchangeTexture2DFactoryNode`。

2.  **管线执行阶段 (`UAxFInterchangePipeline::ExecutePipeline`)**:
    - 在翻译完成后，`UAxFInterchangePipeline` 被执行。
    - 它遍历节点容器，找到 `UAxFMaterialObjectNode`。
    - 根据节点中的 `PayloadData`（如 `UsedFeatures` 列表），它会创建相应的 `UInterchangeShaderGraphNode`，并设置 Substrate 材质所需的复杂节点网络（如清漆、各向异性等）。
    - 它还会处理纹理节点，将其与材质图连接。

3.  **后处理阶段 (`ExecutePostImportPipeline`, `ExecutePostFactoryPipeline`)**:
    - 在材质资产被工厂创建后，管线会进行最终调整，例如根据 `bUseTriplanarMappingByDefault` 设置纹理采样器，并创建 `USpecularProfile` 资产。

### 进阶用法（自定义或扩展）

如果需要修改 AxF 的导入行为，可以继承 `UAxFInterchangePipeline` 并重写其虚函数，例如 `ExecutePipeline`，然后在导入时选择自定义的管线。

## Demo 示例

由于此插件深度集成于 Interchange 框架，没有独立的运行时组件。以下是一个概念性的示例，展示如何在代码中检查一个节点是否为 AxF 材质节点（通常在自定义管线或后处理器中使用）。

```cpp
// MyCustomPipeline.h
#pragma once
#include "AxFInterchangePipeline.h"
#include "MyCustomPipeline.generated.h"

UCLASS()
class UMyCustomAxFPipeline : public UAxFInterchangePipeline
{
    GENERATED_BODY()

protected:
    virtual void ExecutePipeline(
        UInterchangeBaseNodeContainer* BaseNodeContainer,
        TArray<UInterchangeSourceData*> const& SourceDatas,
        FString const& ContentBasePath) override
    {
        // 先调用父类的默认处理逻辑
        Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

        // 遍历所有节点，查找 AxF 材质节点并进行自定义处理
        TArray<UInterchangeBaseNode*> Nodes;
        BaseNodeContainer->GetNodes(Nodes);
        for (UInterchangeBaseNode* Node : Nodes)
        {
            if (UAxFMaterialObjectNode* AxFNode = Cast<UAxFMaterialObjectNode>(Node))
            {
                // 获取 AxF 材质数据
                const UE::Interchange::FAxFMaterialObjectData& Data = AxFNode->PayloadData;
                
                // 例如，检查是否使用了“清漆”特性
                if (Data.UsedFeatures.Contains(EAxFFeature::ClearCoat))
                {
                    UE_LOG(LogTemp, Log, TEXT("Importing AxF material with ClearCoat feature: %s"), *AxFNode->GetDisplayLabel());
                    // 在这里可以添加自定义逻辑，比如修改后续生成的材质图
                }
            }
        }
    }
};
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 依赖项和代码包含关系推断：

| 模块 | 用途 |
|---|---|
| `Interchange` | 核心的资产交换框架，提供翻译器、管线、节点容器等基础架构。 |
| `InterchangeAxFAssets` | 提供 AxF 相关的资产类型定义和工厂（如 `UAxFMaterialObjectNode` 的工厂）。 |
| `Engine` (SpecularProfile) | 用于创建和管理 `USpecularProfile` 资产，这是 Substrate 材质系统的一部分。 |

## 维护状态

### 近期更新

```
- 2026-04-15 b5257e84 Linux: Fix compile errors
- 2026-04-14 35e60df1 Migrate UE_LOG to UE_LOGF.
- 2026-04-10 43da9049 Fix warning
```

### 维护评价

- **创建时间**：2026年3月，是一个非常新的插件。
- **最近更新**：最近一个月内有多次提交，但主要是**编译错误修复、日志格式迁移和警告修复**，属于维护性更新，未见新功能添加。
- **活跃状态**：处于**早期活跃维护**阶段。作为实验性插件，其核心功能已实现，当前重点在于稳定性和跨平台兼容性。
- **已知限制**：
    1.  **实验性**：标记为 `IsExperimentalVersion=true`，且默认未安装（`Installed=false`），意味着 API 和功能可能在未来版本中发生变化。
    2.  **依赖链**：依赖于 `Interchange` 和 `InterchangeAxFAssets` 两个插件，需要确保它们一同启用。
    3.  **平台支持**：支持 Win64, Linux, Mac。
- **推荐使用**：如果你的项目**必须**导入 X-Rite Pantora 的 AxF 材质，并且愿意接受实验性插件的潜在风险，那么可以使用。对于大多数项目，建议关注其后续版本的稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InterchangeAxF)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中发现)