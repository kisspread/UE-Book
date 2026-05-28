# Semantic Search Toolset

> Exposes the SemanticSearch plugin's hybrid vector+BM25 asset search as an AI Toolset Registry tool.

| 属性 | 值 |
|---|---|
| 中文名 | 语义搜索工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SemanticSearchToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SemanticSearchToolset) | |

## 用途

这个插件是 **SemanticSearch** 插件与 **AI Toolset Registry** 之间的桥梁。

SemanticSearch 插件会为项目中的资产（蓝图、静态网格体、骨骼网格体、纹理、材质、材质实例）建立向量嵌入索引，支持基于自然语言的语义搜索。而这个工具集插件将搜索能力封装为 AI Toolset Registry 可调用的工具，使得 AI Agent 能够通过自然语言查询找到项目中最相关的资产。

插件提供两种搜索模式：
- **混合搜索（Search）**：结合向量相似度 + BM25 文本匹配，适合自然语言描述性查询
- **相似搜索（FindSimilar）**：纯向量相似度匹配，找到与指定资产语义相似的其他资产

## 使用场景

- 你正在构建一个 AI 辅助的资产查找系统 → 让 AI Agent 通过自然语言在 Content Browser 中搜索资产
- 你想为大型项目建立智能资产推荐 → 用 FindSimilar 找到与某个资产语义相似的其他资产
- 你在开发基于 Toolset Registry 的 AI 工作流 → 将语义搜索作为其中一个可调用工具

## 蓝图用法

本插件的函数标记为 `AICallable`（而非 `BlueprintCallable`），主要面向 AI Toolset Registry 调用，而非直接在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Search` | 对已索引资产执行自然语言混合搜索（向量 + BM25） | `USemanticSearchToolset` |
| `FindSimilar` | 查找与指定资产语义相似的资产（仅向量匹配） | `USemanticSearchToolset` |

### 参数说明

两个函数共享以下过滤参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| `Query` | `FString` | 自然语言查询文本，不能为空 |
| `AssetPath` | `FSoftObjectPath` | 参考资产路径（仅 FindSimilar） |
| `ClassFilter` | `TArray<UClass*>` | 类过滤数组，传空数组则搜索所有已索引类 |
| `PathRegexes` | `TArray<FString>` | 路径正则过滤，传空数组则搜索所有路径 |
| `K` | `int32` | 最大返回结果数，默认 10 |

**支持的资产基类**：Blueprint、StaticMesh、SkeletalMesh、Texture、Material、MaterialInstance。传入基类会覆盖其所有子类。

### 返回值

两个函数均返回 `USemanticSearchAsyncResult*`，包含 `TArray<FSemanticSearchResult>` 结果，按相关度从高到低排序。

`FSemanticSearchResult` 结构体：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Path` | `FSoftObjectPath` | 资产完整路径，如 `/Game/Blueprints/BP_Foo.BP_Foo` |
| `Class` | `TObjectPtr<UClass>` | 资产类 |
| `Caption` | `FString` | 索引时由 SemanticSearch 插件生成的资产描述 |

## C++ 用法

### 头文件引入

```cpp
#include "SemanticSearchToolset.h"
```

### 基本用法

这两个函数是 `UToolsetDefinition` 的成员（标记为 `AICallable`），通常由 AI Toolset Registry 框架自动调用。若需直接调用：

```cpp
// 基本搜索：用自然语言查询资产
USemanticSearchAsyncResult* SearchTask = USemanticSearchToolset::Search(
    TEXT("blueprint with player movement logic"),  // 自然语言查询
    {},                                              // 不过滤类
    {},                                              // 不过滤路径
    5                                                // 返回前 5 个结果
);

// 带类过滤的搜索：只搜索蓝图和材质
TArray<UClass*> ClassFilter = { UBlueprint::StaticClass(), UMaterial::StaticClass() };
USemanticSearchAsyncResult* FilteredSearch = USemanticSearchToolset::Search(
    TEXT("red metallic surface"),
    ClassFilter,
    {},
    10
);
```

### 进阶用法

```cpp
// 带路径正则过滤的相似资产查找
TArray<FString> PathFilters = {
    TEXT("^/Game/Characters/.*"),   // 只搜索 Characters 目录
    TEXT("^/Game/Weapons/.*")       // 及 Weapons 目录
};
USemanticSearchAsyncResult* SimilarTask = USemanticSearchToolset::FindSimilar(
    FSoftObjectPath(TEXT("/Game/Characters/Hero/HeroMesh.HeroMesh")),
    {},
    PathFilters,
    20
);
```

### 过滤工具函数

```cpp
#include "SemanticSearchFilter.h"

using namespace UE::SemanticSearchToolset;

// 展开类过滤器（包含子类匹配）
TSet<FName> AllowedNames;
int32 Unresolved = ExpandClassFilter(ClassFilter, SupportedClassNames, AllowedNames);

// 编译并匹配路径正则
TArray<FRegexPattern> Patterns;
int32 FailedCount = CompileRegexPatterns(RegexStrings, Patterns);
bool bMatches = MatchesPathRegex(AssetPath, Patterns);
```

## Demo 示例

本插件不直接面向用户使用，而是作为 AI Toolset Registry 的工具定义层。以下展示如何在自定义 Toolset 中扩展语义搜索逻辑：

```cpp
// MyCustomSearchToolset.h
#pragma once

#include "CoreMinimal.h"
#include "SemanticSearchToolset.h"
#include "MyCustomSearchToolset.generated.h"

UCLASS()
class UMyCustomSearchToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    // 包装 Search 以添加自定义逻辑
    UFUNCTION(meta = (AICallable), Category = "CustomSearch")
    static USemanticSearchAsyncResult* SearchInCharacterFolder(
        const FString& Query,
        int32 MaxResults = 10)
    {
        // 限定只搜索角色相关资产
        TArray<FString> PathFilters = { TEXT("^/Game/Characters/.*") };
        return USemanticSearchToolset::Search(Query, {}, PathFilters, MaxResults);
    }
};
```

## 模块依赖

Build.cs 中仅依赖 `Core`，但插件级别依赖以下插件：

| 插件 | 用途 |
|---|---|
| `ToolsetRegistry` | AI 工具注册框架，提供 `UToolsetDefinition` 基类和异步工具调用机制 |
| `SemanticSearch` | 语义搜索引擎，提供资产索引和向量+BM25 混合搜索能力 |

无特殊模块依赖（仅标准 Core 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `cfe535bd` | Move Semantic Search Toolset out of NFL and into Experimental | 将插件从 NFL 内部迁移至公开的 Experimental 目录 |

### 维护评价

- **创建时间**：2026-05-21，非常新的插件
- **更新频率**：仅有 1 次提交，为初次入库
- **维护状态**：🆕 刚刚发布，尚无后续更新
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需手动启用
- **推荐程度**：作为 Experimental 阶段的工具集成层，适合对 AI 辅助资产搜索感兴趣的早期探索者。**不建议在生产环境中依赖此插件**，API 可能发生较大变化。

⚠️ 这是一个实验性插件，仅有一个初始提交，接口可能不稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SemanticSearchToolset)
- [SemanticSearch 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SemanticSearch)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)