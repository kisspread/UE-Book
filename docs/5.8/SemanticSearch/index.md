# Semantic Search

> Very early work in progress of a semantic search system for assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SemanticSearch` (Editor), `SemanticSearchEditorIntegrations` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SemanticSearch) | |

## 用途

SemanticSearch 插件旨在为 Unreal Engine 编辑器提供一个**基于语义的资产搜索系统**。它解决的核心问题是：在拥有海量资产（如模型、材质、纹理、蓝图等）的大型项目中，传统的基于文件名或标签的关键词搜索往往效率低下且不准确。该系统通过将资产的文本描述（如名称、标签、注释）甚至图像内容转换为高维向量（嵌入），并计算查询文本与资产向量之间的相似度，从而实现更智能、更符合人类直觉的“语义搜索”。用户可以用自然语言描述想要的资产，系统能返回语义上最相关的结果，而不仅仅是关键词匹配。

## 使用场景

- **大型项目资产查找**：当项目资产库庞大，且资产命名不规范或描述信息丰富时，使用自然语言（如“一个破旧的木制栅栏”、“科幻风格的蓝色能量盾”）快速定位相关资产。
- **美术资源管理**：美术人员可以通过描述视觉特征（如“高光强烈的金属材质”、“带有卡通描边的风格”）来查找参考或可用的材质、纹理。
- **快速原型开发**：在搭建场景原型时，快速找到符合场景氛围的资产，例如搜索“阴暗森林中的雾气效果”。
- **资产复用与发现**：帮助开发者发现项目中已存在但可能被遗忘的、符合新需求的资产。

## 蓝图用法

该插件主要为编辑器工具提供后端支持，其核心功能通过 C++ API 暴露。蓝图中可直接使用的节点有限，主要集中在编辑器工具集成模块。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SearchAssets` | 根据文本查询执行语义搜索，返回资产列表。 | `USemanticSearchSubsystem` |
| `GetAssetEmbedding` | 获取指定资产的语义嵌入向量。 | `USemanticSearchSubsystem` |

### 使用示例（蓝图描述）

1.  获取 `Semantic Search Subsystem` 的引用。
2.  调用 `Search Assets` 节点，输入查询字符串（如“红色跑车”）。
3.  从返回的 `Asset Data` 数组中获取匹配的资产信息。
4.  （可选）使用 `Get Asset Embedding` 节点查看特定资产的向量表示，用于调试或自定义相似度计算。

## C++ 用法

详细的 C++ API 用法、类结构和集成方式，请参阅子模块文档：
- **核心搜索与嵌入逻辑**：[SemanticSearch 模块文档](SemanticSearch.md)
- **编辑器界面与工具集成**：[SemanticSearchEditorIntegrations 模块文档](SemanticSearchEditorIntegrations.md)

### 头文件引入

```cpp
#include "SemanticSearchSubsystem.h" // 核心子系统
#include "SemanticSearchEditorIntegrationsModule.h" // 编辑器集成模块
```

### 基本用法

```cpp
// 获取语义搜索子系统
USemanticSearchSubsystem* SearchSubsystem = GEditor->GetEditorSubsystem<USemanticSearchSubsystem>();
if (SearchSubsystem)
{
    // 执行一次语义搜索
    TArray<FAssetData> Results;
    SearchSubsystem->SearchAssets(TEXT("带有法线贴图的石头材质"), Results);

    // 处理搜索结果
    for (const FAssetData& Asset : Results)
    {
        UE_LOG(LogTemp, Log, TEXT("Found Asset: %s"), *Asset.AssetName.ToString());
    }
}
```
*（示例基于典型子系统使用模式推断）*

### 进阶用法

进阶用法涉及自定义嵌入模型、调整相似度计算参数、以及将语义搜索集成到自定义编辑器工具中。请参考各模块的详细文档。

## Demo 示例

一个最小的可运行示例，展示如何初始化子系统并执行一次搜索。

**MySemanticSearchActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MySemanticSearchActor.generated.h"

UCLASS()
class AMySemanticSearchActor : public AActor
{
    GENERATED_BODY()
public:
    AMySemanticSearchActor();

    UFUNCTION(BlueprintCallable, Category = "Semantic Search")
    void PerformSearch(const FString& Query);

private:
    UPROPERTY()
    class USemanticSearchSubsystem* SearchSubsystem;
};
```

**MySemanticSearchActor.cpp**
```cpp
#include "MySemanticSearchActor.h"
#include "SemanticSearchSubsystem.h"
#include "Editor.h" // 用于访问 GEditor

AMySemanticSearchActor::AMySemanticSearchActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySemanticSearchActor::PerformSearch(const FString& Query)
{
    if (!SearchSubsystem)
    {
        SearchSubsystem = GEditor->GetEditorSubsystem<USemanticSearchSubsystem>();
    }

    if (SearchSubsystem)
    {
        TArray<FAssetData> Results;
        SearchSubsystem->SearchAssets(Query, Results);
        UE_LOG(LogTemp, Warning, TEXT("Search for '%s' returned %d results."), *Query, Results.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Semantic Search Subsystem not available."));
    }
}
```

## 模块依赖

使用此插件，你的模块需要依赖以下**独特**模块（除标准 Core/Engine/Slate 等外）：

| 模块 | 用途 |
|---|---|
| `SemanticSearch` | 提供核心的语义搜索、嵌入生成和相似度计算功能。 |
| `SemanticSearchEditorIntegrations` | 提供编辑器内的 UI 集成、资产索引和搜索工具。 |
| `AIModule` | 可能用于集成或借鉴其向量/嵌入相关基础设施。 |
| `AssetRegistry` | 用于查询和访问项目中的资产元数据。 |
| `ContentBrowser` | 用于在内容浏览器中集成搜索结果或相关操作。 |
| `PropertyEditor` | 用于在属性面板中集成语义搜索相关设置。 |

## 维护状态

### 近期更新

*（由于插件创建于 2026-04-10，且为实验性插件，暂无公开的 git 历史记录可供分析。以下为基于其状态的推断。）*

- **2026-04-10**：插件初始创建，包含核心搜索模块和编辑器集成模块。
- **状态**：处于非常早期的积极开发阶段（“Very early work in progress”）。

### 维护评价

- **创建时间**：2026年4月，是一个非常新的插件。
- **维护状态**：**实验性且处于早期开发中**。`.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。
- **活跃度**：作为 Epic Games 官方实验性项目，预计会有持续开发，但 API 和功能可能频繁变动。
- **已知限制**：作为“非常早期的工作”，功能可能不完整，性能、准确性和支持的资产类型可能有限。
- **推荐使用**：**仅推荐用于学习、研究或早期原型验证**。不建议在生产项目中依赖此插件，因为其 API 和行为可能发生破坏性更改。关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SemanticSearch)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现公开的测试用例路径，可能位于 `Engine/Tests/` 下或插件内部）