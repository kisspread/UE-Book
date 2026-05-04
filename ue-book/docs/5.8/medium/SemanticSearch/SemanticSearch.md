```markdown
# Semantic Search

> Very early work in progress of a semantic search system for assets

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

Semantic Search 是一个基于 AI 嵌入（Embedding）的资产语义搜索系统。它解决的核心问题是：**在大型项目中，如何通过自然语言描述或语义相似性来查找资产**，而不仅仅依赖传统的文件名/路径匹配。

系统的工作流程如下：

1. **资产处理**：内置的资产处理器（Blueprint、Material、StaticMesh、SkeletalMesh、Texture、MaterialInstance）从资产中提取缩略图和结构化元数据
2. **字幕生成**：通过远程 MLS 后端服务，将资产缩略图和元数据发送给 AI 模型，生成自然语言描述（Caption）和关键词（Keywords）
3. **嵌入生成**：将文本描述转换为高维向量嵌入（Embedding）
4. **混合索引**：同时维护向量索引（FAISS，支持 Flat 精确搜索和 PQ 乘积量化压缩搜索）和 BM25 文本倒排索引，通过 Reciprocal Rank Fusion（RRF）融合两种搜索结果
5. **派生数据缓存**：所有生成的嵌入和字幕都缓存在 DDC（Derived Data Cache）中，避免重复调用后端

该插件需要外部 MLS 后端服务支持，通过 HTTP API 进行通信。

## 使用场景

- 你在做一个大型项目，资产数量成千上万，想用自然语言描述来搜索资产（如"红色金属材质"、"角色骨骼网格"）
- 你需要基于语义相似性查找资产，而不仅仅是文件名匹配
- 你想在编辑器中集成 AI 驱动的资产搜索功能
- 你需要对资产进行自动标注和分类

## 蓝图用法

该插件没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` API。所有功能均为 C++ 层面的编辑器集成。

## C++ 用法

### 头文件引入

```cpp
#include "ISemanticSearchModule.h"
#include "HybridSearchIndex.h"
#include "AssetProcessorManager.h"
#include "Settings/SemanticSearchSettings.h"
```

### 基本用法 — 模块接口

通过 `ISemanticSearchModule` 接口与系统交互：

```cpp
// 获取模块实例
UE::SemanticSearch::ISemanticSearchModule& Module = UE::SemanticSearch::ISemanticSearchModule::Get();

// 注册自定义嵌入提供者
Module.RegisterEmbeddingProvider(MakeUnique<FMyEmbeddingProvider>());

// 索引单个资产
FAssetData AssetData = /* ... */;
Module.IndexAsset(AssetData);

// 索引所有资产（强制重建）
Module.IndexAllAssets(/* bForceBuild = */ true);

// 获取索引统计信息
UE::SemanticSearch::FSemanticSearchIndexStats Stats = Module.GetIndexStats();
UE_LOG(LogTemp, Log, TEXT("向量数量: %d, BM25 数量: %d, 维度: %d"),
    Stats.VectorCount, Stats.BM25Count, Stats.Dimension);

// 切换索引类型（Flat 或 PQ）
Module.SwitchIndexType(UE::SemanticSearch::ESemanticSearchIndexType::PQ);

// 重训练量化索引（生成新的码本）
Module.RetrainIndex();
```

### 基本用法 — 混合搜索

```cpp
#include "HybridSearchIndex.h"

// 获取混合搜索索引单例
UE::SemanticSearch::FHybridSearchIndex& SearchIndex = UE::SemanticSearch::FHybridSearchIndex::Get();

// 执行混合搜索（文本 + 向量融合）
FString QueryText = TEXT("red metallic material");
TArray<float> QueryEmbedding = /* 从嵌入提供者获取的查询向量 */;
int32 TopK = 20;

TArray<UE::SemanticSearch::FHybridSearchResult> Results = SearchIndex.Search(
    QueryText, QueryEmbedding, TopK);

for (const auto& Result : Results)
{
    UE_LOG(LogTemp, Log, TEXT("ID: %lld, RRF Score: %.4f, Vector Dist: %.4f, BM25: %.4f"),
        Result.ID, Result.RRFScore, Result.VectorDistance, Result.BM25Score);
}
```

### 基本用法 — 资产处理器管理

```cpp
#include "AssetProcessorManager.h"

// 获取处理器管理器单例
UE::SemanticSearch::FAssetProcessorManager& Manager = UE::SemanticSearch::FAssetProcessorManager::Get();

// 注册自定义资产处理器
Manager.RegisterAssetProcessor<FMyCustomProcessor>();

// 获取某个资产对应的处理器
FAssetData AssetData = /* ... */;
TSharedPtr<UE::SemanticSearch::IAssetProcessor> Processor = Manager.GetProcessorForAsset(AssetData);

// 异步获取资产的字幕数据
Manager.GetCaptionData(AssetData,
    [](UE::SemanticSearch::FAssetCaptionResult&& Result, FString&& Error)
    {
        if (Error.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("Caption: %s"), *Result.Caption);
        }
    });

// 异步获取资产的嵌入数据
Manager.GetEmbeddingData(AssetData,
    [](UE::SemanticSearch::FAssetEmbeddingResult&& Result, FString&& Error)
    {
        if (Error.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("Embedding 维度: %d"), Result.Embedding.Num());
        }
    });
```

### 进阶用法 — 自定义资产处理器

```cpp
// MyAssetProcessor.h
#pragma once
#include "Implementations/ThumbnailBaseProcessor.h"

class FMyAssetProcessor : public UE::SemanticSearch::FThumbnailBaseAssetProcessor
{
public:
    constexpr virtual FStringView GetProcessSubBucketName() const override
    {
        return TEXTVIEW("FMyAssetProcessor");
    }

    virtual UClass& GetSupportedClass() const override;
    virtual bool SupportDerivedClasses() const override { return false; }

    virtual TSharedPtr<FJsonObject> GetMetadata(
        const TSharedRef<const FAssetData>& InAsset) const override;
};
```

```cpp
// MyAssetProcessor.cpp
#include "MyAssetProcessor.h"
#include "MyAssetClass.h"

UClass& FMyAssetProcessor::GetSupportedClass() const
{
    return *UMyAssetClass::StaticClass();
}

TSharedPtr<FJsonObject> FMyAssetProcessor::GetMetadata(
    const TSharedRef<const FAssetData>& InAsset) const
{
    TSharedPtr<FJsonObject> Metadata = MakeShared<FJsonObject>();

    // 使用辅助函数从 AssetDataTag 提取元数据
    UE::SemanticSearch::Private::SetMetadata(
        Metadata, InAsset, FName("MyTag"), TEXTVIEW("my_metadata_key"));

    return Metadata;
}
```

### 进阶用法 — 向量索引直接操作

```cpp
#include "VectorIndex/VectorIndexFactory.h"
#include "Interfaces/IVectorIndex.h"
#include "Interfaces/IQuantizedVectorIndex.h"

// 创建 Flat 索引（精确搜索，无需训练）
TSharedPtr<UE::SemanticSearch::IVectorIndex> FlatIndex =
    UE::SemanticSearch::CreateVectorIndex(
        UE::SemanticSearch::ESemanticSearchIndexType::Flat, 768, nullptr);

// 创建 PQ 索引（压缩搜索，需要训练）
const USemanticSearchSettings* Settings = USemanticSearchSettings::Get();
TSharedPtr<UE::SemanticSearch::IVectorIndex> PQIndex =
    UE::SemanticSearch::CreateVectorIndex(
        UE::SemanticSearch::ESemanticSearchIndexType::PQ, 768, Settings);

// 训练 PQ 索引（需要代表性向量）
TArray<float> TrainingVectors = /* 收集训练数据 */;
PQIndex->Train(TrainingVectors, TrainingVectors.Num() / 768);

// 添加向量
TArray<int64> IDs = { 1, 2, 3 };
TArray<float> Vectors = /* 对应的向量数据 */;
PQIndex->Add(IDs, Vectors);

// 搜索最近邻
TArray<float> QueryVector = /* 查询向量 */;
TArray<UE::SemanticSearch::FSearchResult> SearchResults =
    PQIndex->Search(QueryVector, 10);

// 量化向量（仅 PQ 索引支持）
if (PQIndex->SupportsQuantization())
{
    auto* QuantizedIndex = static_cast<UE::SemanticSearch::IQuantizedVectorIndex*>(PQIndex.Get());
    TArray<uint8> QuantizedCodes = QuantizedIndex->Quantize(Vectors, IDs.Num());
    QuantizedIndex->AddQuantized(IDs, QuantizedCodes);
}
```

### 进阶用法 — BM25 文本索引

```cpp
#include "TextIndex/BM25Index.h"

UE::SemanticSearch::FBM25Index BM25;

// 添加文档（资产路径、字幕、关键词）
BM25.Add(1, TEXT("/Game/Materials/M_RedMetal"), TEXT("Red metallic material with scratches"),
    { TEXT("red"), TEXT("metal"), TEXT("scratched") });

BM25.Add(2, TEXT("/Game/Materials/M_BluePlastic"), TEXT("Blue smooth plastic surface"),
    { TEXT("blue"), TEXT("plastic"), TEXT("smooth") });

// 搜索
TArray<UE::SemanticSearch::FBM25Result> Results = BM25.Search(TEXT("red metal"), 5);
for (const auto& Result : Results)
{
    UE_LOG(LogTemp, Log, TEXT("ID: %lld, Score: %.4f"), Result.ID, Result.Score);
}

// 序列化/反序列化
FMemoryWriter Writer(/* ... */);
BM25.Serialize(Writer);

FMemoryReader Reader(/* ... */);
TUniquePtr<UE::SemanticSearch::FBM25Index> Loaded = UE::SemanticSearch::FBM25Index::Deserialize(Reader);
```

## Demo 示例

一个完整的自定义资产处理器示例：

```cpp
// FCustomAssetProcessor.h
#pragma once

#include "Implementations/ThumbnailBaseProcessor.h"
#include "Dom/JsonObject.h"

namespace UE::SemanticSearch::Private
{

class FCustomAssetProcessor : public FThumbnailBaseAssetProcessor
{
public:
    constexpr virtual FStringView GetProcessSubBucketName() const override
    {
        return TEXTVIEW("FCustomAssetProcessor");
    }

    virtual UClass& GetSupportedClass() const override;
    virtual bool SupportDerivedClasses() const override { return false; }

    virtual TSharedPtr<FJsonObject> GetMetadata(
        const TSharedRef<const FAssetData>& InAsset) const override;
};

} // namespace UE::SemanticSearch::Private
```

```cpp
// FCustomAssetProcessor.cpp
#include "CustomAssetProcessor.h"
#include "AssetProcessors/AssetProcessorUtils.h"
#include "MyGameAsset.h"

namespace UE::SemanticSearch::Private
{

UClass& FCustomAssetProcessor::GetSupportedClass() const
{
    return *UMyGameAsset::StaticClass();
}

TSharedPtr<FJsonObject> FCustomAssetProcessor::GetMetadata(
    const TSharedRef<const FAssetData>& InAsset) const
{
    TSharedPtr<FJsonObject> Metadata = MakeShared<FJsonObject>();

    // 从资产的 AssetDataTags 中提取自定义标签
    SetMetadata(Metadata, InAsset, FName("Category"), TEXTVIEW("category"));
    SetMetadata(Metadata, InAsset, FName("Description"), TEXTVIEW("description"));

    return Metadata;
}

} // namespace UE::SemanticSearch::Private
```

注册处理器（在模块启动时调用）：

```cpp
#include "AssetProcessorManager.h"
#include "CustomAssetProcessor.h"

void RegisterMyProcessor()
{
    UE::SemanticSearch::FAssetProcessorManager::Get()
        .RegisterAssetProcessor<UE::SemanticSearch::Private::FCustomAssetProcessor>();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | 派生数据缓存，用于存储和检索嵌入/字幕数据 |
| `HTTP` | 远程嵌入提供者的 HTTP 通信 |
| `Json` | 资产元数据的 JSON 序列化 |
| `FAISS` | 第三方向量相似性搜索库（Flat 和 PQ 索引的底层实现） |

## 维护状态

### 近期更新

由于该插件创建于 2026-04-10（未来日期），无法获取实际的 git log 信息。以下基于源码分析推断：

- 插件标记为 `IsExperimentalVersion: true`，`EnabledByDefault: false`
- 版本号为 `0.1`，描述中明确标注"Very early work in progress"
- 代码结构完整，包含 48 个源文件，涵盖完整的资产处理、索引、搜索管线

### 维护评价

- **实验性插件**：标记为实验性版本，默认未启用，需要手动在插件设置中激活
- **早期开发阶段**：版本号 0.1，描述明确为"非常早期的工作进展"
- **依赖外部服务**：需要 MLS 后端服务支持，无法独立运行
- **代码质量较高**：尽管是早期版本，代码结构清晰，接口设计合理，使用了 FAISS 库进行向量搜索，支持 DDC 缓存
- **功能完整度**：已支持 6 种资产类型（Blueprint、Material、MaterialInstance、SkeletalMesh、StaticMesh、Texture），支持 Flat 和 PQ 两种索引类型，支持混合搜索（向量 + BM25 + RRF 融合）
- **⚠️ 警告**：此插件处于实验性早期阶段，API 可能发生重大变化，不建议在生产环境中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SemanticSearch)
- [官方文档]()（暂无）
```