# Cinematic Assembly Tools (CAT)

> CAT is a suite of cinematic pipeline tools for shot management and linear content creation

| 属性 | 值 |
|---|---|
| 中文名 | 电影组装工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CineAssemblyTools` (Runtime), `CineAssemblyToolsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CinematicAssemblyTools) | |

## 用途

CinematicAssemblyTools (CAT) 插件提供了一套完整的工具，用于管理复杂的线性内容创作管线（如电影预览、电视广告、虚拟制片项目）。它超越了简单的镜头管理，定义了一个名为“CineAssembly”的核心资产，该资产继承自 `ULevelSequence`，但增加了丰富的结构化数据。

CineAssembly 可以：
1.  **关联场景（Level）**：明确指定该序列应在哪个关卡中播放。
2.  **管理子组件（Sub-Assemblies）**：支持层级结构，一个主组装可以包含多个子组装（如场景、镜头、特效片段），便于组织和导航。
3.  **关联资产**：可以在创建组装时，根据“模式”（Schema）自动生成并关联其他资产（如音频、后期效果预设、参考视频）。
4.  **强大的元数据系统**：支持结构化元数据（字符串、布尔、整数、浮点、资产路径、其他CineAssembly引用），并通过令牌（Token）系统实现在资产命名和路径中的动态替换，极大提升了管线的自动化和一致性。

该插件解决的核心问题是：在影视级虚拟制片项目中，如何标准化、结构化地创建、组织和维护大量的序列资产及其关联资源，确保管线各环节（预演、拍摄、后期）能够高效协作。

## 使用场景

-   你正在制作一个线性叙事内容（如电影预览、过场动画、VR体验），需要管理数十到数百个镜头和场景 → 用 CineAssembly 替代独立的 Level Sequence，建立清晰的层级结构和元数据。
-   你的项目需要标准化资产创建流程：创建一个镜头序列时，必须同时创建对应的音频轨道、后期调色预设和参考板 → 使用 CineAssemblySchema 预定义关联资产模板，一键生成完整资产包。
-   你需要在资产命名和保存路径中动态插入序列名称、制作版本、导演备注等信息 → 使用 CineAssembly 的令牌（Token）和元数据系统。
-   你在构建一个虚拟制片管理系统，需要查询和批量操作具有特定属性（如特定导演、特定场景）的序列资产 → 利用 CineAssembly 注册到资产注册表（Asset Registry）的丰富标签进行搜索和过滤。

## 蓝图用法

### 核心节点

#### 组装（CineAssembly）管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Schema` | 获取此组装基于的模式（Schema）资产。 | `UCineAssembly` |
| `Initialize From Schema` | 根据输入的模式初始化此组装，可选择是否复制模式中的 MovieScene。 | `UCineAssembly` |
| `Initialize From Template` | 根据一个模板关卡序列初始化此组装。 | `UCineAssembly` |
| `Get Level` / `Set Level` | 获取或设置此组装关联的关卡（World）。 | `UCineAssembly` |
| `Get Parent Assembly` / `Set Parent Assembly` | 获取或设置父级组装，建立层级关系。 | `UCineAssembly` |
| `Get Label` / `Set Label` | 获取或设置用于标识此组装的语义标签（如“MainStory”、“BossFight”）。 | `UCineAssembly` |
| `Get Sub-Assemblies` | 获取所有直接的子组装数组。 | `UCineAssembly` |
| `Find Sub-Assemblies By Label` | 根据标签查找所有匹配的子组装。 | `UCineAssembly` |
| `Get Associated Assets` | 获取由此组装关联的所有资产。 | `UCineAssembly` |
| `Find Associated Assets By Label` | 根据标签查找所有匹配的关联资产。 | `UCineAssembly` |
| `Get Author` / `Set Author` | (仅编辑器) 获取或设置组装的创建者信息。 | `UCineAssembly` |
| `Get Created String` | (仅编辑器) 获取组装的创建时间格式化字符串。 | `UCineAssembly` |
| `Get Note Text` / `Set Note Text` / `Append To Note Text` | 获取、设置或追加此组装的用户备注。 | `UCineAssembly` |
| `Get Production Name` | 获取此组装关联的影视项目名称。 | `UCineAssembly` |

#### 元数据操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Metadata As String` / `Get Metadata As String` | 以字符串形式设置或获取元数据。 | `UCineAssembly` |
| `Set Metadata As Bool` / `Get Metadata As Bool` | 以布尔值形式设置或获取元数据。 | `UCineAssembly` |
| `Set Metadata As Integer` / `Get Metadata As Integer` | 以整数形式设置或获取元数据。 | `UCineAssembly` |
| `Set Metadata As Float` / `Get Metadata As Float` | 以浮点数形式设置或获取元数据。 | `UCineAssembly` |
| `Apply Metadata` | 从一个键值对映射（TMap）批量应用元数据，类型由模式定义。 | `UCineAssembly` |
| `Get Full Metadata String` | 获取所有元数据格式化后的 JSON 字符串，便于调试和显示。 | `UCineAssembly` |

#### 模式（Schema）管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Default Assembly Path` / `Set Default Assembly Path` | 获取或设置基于此模式创建的组装的默认保存路径。 | `UCineAssemblySchema` |
| `Get Default Level` / `Set Default Level` | 获取或设置基于此模式创建的组装的默认关联关卡。 | `UCineAssemblySchema` |
| `Get Default Folders` | 获取基于此模式创建的组装时需要默认创建的文件夹列表。 | `UCineAssemblySchema` |
| `Add Default Folder` / `Remove Default Folder` | 添加或移除默认文件夹。 | `UCineAssemblySchema` |

### 使用示例（蓝图描述）

1.  **根据模式创建新组装**：
    1.  使用 `Construct Object` 节点创建一个 `CineAssembly` 资产。
    2.  将一个已配置好的 `CineAssemblySchema` 资产作为输入。
    3.  调用 `Initialize From Schema` 节点，并传入该 Schema 资产。
    4.  此时，新创建的 CineAssembly 已经包含 Schema 指定的所有默认设置、关联资产定义和子组装模板。

2.  **设置和查询结构化元数据**：
    1.  对一个 CineAssembly 对象调用 `Set Metadata As String (Key: “Director”, Value: “张三”)`。
    2.  调用 `Set Metadata As Float (Key: “EstimatedDuration”, Value: 3.5)`。
    3.  稍后，使用 `Get Metadata As String` 并提供键“Director”来查询导演信息。
    4.  使用 `Get Full Metadata String` 可以一次性获取所有元数据，用于保存到文件或发送给外部工具。

## C++ 用法

### 头文件引入

```cpp
#include "CineAssembly.h"
#include "CineAssemblySchema.h"
```

### 基本用法

```cpp
// 1. 获取或创建 CineAssemblySchema
UCineAssemblySchema* MySchema = LoadObject<UCineAssemblySchema>(nullptr, TEXT("/Game/Cinematic/Schemas/MySequenceSchema"));
if (!MySchema)
{
    MySchema = NewObject<UCineAssemblySchema>(GetTransientPackage(), TEXT("NewSchema"));
    MySchema->SchemaName = TEXT("MyCustomSchema");
    // 配置默认元数据字段
    FAssemblyMetadataDesc Desc;
    Desc.Type = ECineAssemblyMetadataType::String;
    Desc.Key = TEXT("Director");
    MySchema->AssemblyMetadata.Add(Desc);
    MySchema->SavePackage(); // 保存为资产
}

// 2. 基于 Schema 创建一个 CineAssembly
UCineAssembly* NewAssembly = NewObject<UCineAssembly>(GetTransientPackage(), NAME_None, RF_Transactional);
NewAssembly->InitializeFromSchema(MySchema);

// 3. 设置基本属性
NewAssembly->SetLevel(TSoftObjectPtr<UWorld>(FSoftObjectPath("/Game/Maps/MainLevel")));
NewAssembly->SetLabel(FName(TEXT("Act1")));
NewAssembly->SetNoteText(TEXT("第一幕开场"));
NewAssembly->SetAuthor(TEXT("导演A"));

// 4. 设置元数据
NewAssembly->SetMetadataAsString(TEXT("Director"), TEXT("李四"));
NewAssembly->SetMetadataAsInteger(TEXT("TakeNumber"), 1);
NewAssembly->SetMetadataAsBool(TEXT("Approved"), false);

// 5. 查询
const UCineAssemblySchema* Schema = NewAssembly->GetSchema();
FString Director;
bool bFound = NewAssembly->GetMetadataAsString(TEXT("Director"), Director);
TArray<UCineAssembly*> SubAssemblies = NewAssembly->GetSubAssemblies();

// 6. 保存组装资产
FString PackageName = TEXT("/Game/Cinematic/Shots/Shot001");
UPackage* Package = CreatePackage(*PackageName);
NewAssembly->Rename(*FPackageName::GetLongPackageAssetName(PackageName), Package);
NewAssembly->SetExternalPackage(Package);
NewAssembly->SavePackage();
```
*（概念代码，演示核心流程）*

### 进阶用法：处理令牌（Tokens）

```cpp
// 假设有一个 CineAssembly 对象，其路径模板为 “Shots/{ProductionName}/{AssemblyLabel}”
// 且设置了元数据 “Director”: “王五”

// 使用命名令牌系统解析模板字符串
FString TemplatePath = NewAssembly->PathRelativeToRoot.ToString();
FText ResolvedText = UCineAssemblyNamingTokens::GetResolvedText(TemplatePath, NewAssembly);
// ResolvedText 可能被解析为 “Shots/MyMovie/Act1”

// 也可以手动添加自定义令牌
UCineAssemblyNamingTokens NamingTokens;
NamingTokens.AddMetadataToken(TEXT("Director"));
FText DirectorTokenResult = UCineAssemblyNamingTokens::GetResolvedText(TEXT("{Director}"), NewAssembly);
// DirectorTokenResult 的值为 “王五”
```

## Demo 示例

```cpp
// CineAssemblyDemo.h
#pragma once

#include "CoreMinimal.h"
#include "CineAssembly.h"
#include "CineAssemblySchema.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CineAssemblyDemo.generated.h"

UCLASS()
class UCineAssemblyDemoFunctionLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "CineAssemblyDemo", meta = (WorldContext = "WorldContextObject"))
    static UCineAssembly* CreateDemoAssembly(UObject* WorldContextObject);
};

// CineAssemblyDemo.cpp
#include "CineAssemblyDemo.h"
#include "CineAssemblyNamingTokens.h"

UCineAssembly* UCineAssemblyDemoFunctionLibrary::CreateDemoAssembly(UObject* WorldContextObject)
{
    UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull);
    if (!World) return nullptr;

    // 1. 创建一个 Schema
    UCineAssemblySchema* DemoSchema = NewObject<UCineAssemblySchema>(GetTransientPackage(), TEXT("DemoSchema"));
    DemoSchema->SchemaName = TEXT("Demo Shot Schema");

    // 添加一个字符串元数据字段
    FAssemblyMetadataDesc DirectorDesc;
    DirectorDesc.Type = ECineAssemblyMetadataType::String;
    DirectorDesc.Key = TEXT("Director");
    DemoSchema->AssemblyMetadata.Add(DirectorDesc);

    // 设置默认关卡
    DemoSchema->bOverrideDefaultLevel = true;
    DemoSchema->DefaultLevel = FSoftObjectPath(World->GetPathName());

    // 2. 基于 Schema 创建 Assembly
    UCineAssembly* DemoAssembly = NewObject<UCineAssembly>(GetTransientPackage(), NAME_None, RF_Transactional);
    DemoAssembly->InitializeFromSchema(DemoSchema, false); // false 表示不复制 MovieScene，使用 Schema 的默认模板

    // 3. 配置 Assembly
    DemoAssembly->SetLabel(FName(TEXT("DemoShot")));
    DemoAssembly->SetNoteText(TEXT("This is a programmatically created demo assembly."));
    DemoAssembly->SetMetadataAsString(TEXT("Director"), TEXT("Demo User"));

    // 4. 使用令牌解析名称（演示）
    FString ResolvedName = UCineAssemblyNamingTokens::GetResolvedText(
        TEXT("{AssemblyLabel}"), DemoAssembly).ToString();
    UE_LOG(LogTemp, Log, TEXT("Resolved Assembly Name: %s"), *ResolvedName);

    // 5. 将 Assembly 移动到持久包中以便保存（可选）
    FString PackagePath = TEXT("/Game/Cinematic/Demo/DemoAssembly");
    UPackage* Package = CreatePackage(*PackagePath);
    DemoAssembly->Rename(*FPackageName::GetLongPackageAssetName(PackagePath), Package);
    DemoAssembly->SetExternalPackage(Package);
    // (注意：实际保存需要编辑器上下文)

    UE_LOG(LogTemp, Log, TEXT("Created Demo CineAssembly with Schema: %s"), *DemoSchema->SchemaName);
    UE_LOG(LogTemp, Log, TEXT("Director Metadata: %s"), *DemoAssembly->GetMetadataAsString(TEXT("Director"), FString()));

    return DemoAssembly;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieSceneTools` | 提供基础的 Level Sequence、MovieScene 和轨道编辑相关工具，是 CineAssembly 继承和功能实现的基石。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `534c9605` | ShotManagement: Suppress warnings in output log when a CineAssemblySchema has no thumbnail brush ass | 当模式（Schema）没有缩略图时，抑制输出日志中的警告，优化控制台信息。 |
| 2026-05-14 | `85850dc9` | ShotManagement: Add missing scripting API functions | 补充了缺失的脚本API函数，增强了蓝图和脚本的控制能力。 |
| 2026-05-14 | `1d99acc3` | ShotManagement: Move ProductionFunctionLibrary.h into Public folder and add API exports | 将`ProductionFunctionLibrary.h`移至公开文件夹并导出API，方便外部模块访问。 |
| 2026-05-14 | `c11b4fd1` | ShotManagement: Add missing Cinematic Assembly Tools scripting API | 补全了电影组装工具的脚本接口，完善了功能暴露。 |
| 2026-05-14 | `d1ca5718` | ShotManagement: Remove non-ASCII characters from plugin files | 清理了插件文件中的非ASCII字符，确保代码的通用性和兼容性。 |

### 维护评价

- **创建时间**：2025年4月，是一个相对较新的插件。
- **近期更新**：最新提交集中在2026年5月14日，进行了一系列密集的改进工作，主要围绕**补充API、优化日志、增强可扩展性**。这表明该插件正处于**积极的功能完善和打磨阶段**。
- **维护状态**：**活跃维护中**。从历史提交看，Epic Games 团队正在投入资源，使其成为一个更完整、更稳定的产品。
- **实验性标志**：插件 `.uplugin` 中 `IsExperimentalVersion` 为 `true`，这表明它可能尚未达到最终稳定形态，API 和功能可能在未来版本中发生变化。
- **推荐使用**：**推荐在虚拟制片或大型线性内容项目中评估使用**。它提供了一套强大的结构化资产管理方案，但鉴于其实验性状态，建议在生产环境中谨慎引入，并做好应对未来API变更的准备。它非常适合从项目初期就建立规范的资产管线。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CinematicAssemblyTools)
- [官方文档]() （暂无）
- [测试用例]() （在提供的信息中未发现独立测试文件，测试可能集成在内部或编辑器测试中）