# WebAPI

> Automated generation of web based APIs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | WebAPI自动生成 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、C++代码模板） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI) | |

## 用途

基于源码分析，`WebAPI` 插件的核心功能是**从 OpenAPI/Swagger 规范文件（JSON 或 YAML）自动生成用于 Unreal Engine 的 Web 服务（Web Service）C++ 代码和蓝图资产**。它解决了手动编写大量 HTTP 请求模型、数据序列化/反序列化、以及与 RESTful API 交互的样板代码的繁琐问题。

这个插件通过解析规范文件中的端点（Paths）、操作（Operations）、数据模型（Schemas/Definitions）和参数等信息，自动生成对应的 UE `UWebAPISchema`、`UWebAPIService`、`UWebAPIOperation` 等对象，并可进一步转换为具体的 C++ 类和蓝图节点，使开发者能够快速、准确地与外部 Web API 集成。

## 使用场景

- 你的项目需要与一个提供 OpenAPI/Swagger 规范文件的外部 Web 服务（如 RESTful API）进行集成。
- 你需要快速原型化或集成多个第三方 API，并希望保持代码与 API 定义同步。
- 你希望避免手动编写网络请求、响应解析和模型类的繁琐工作，并希望利用自动生成的代码来减少错误。
- 当 API 规范更新时，你可以通过重新生成代码来快速同步更新。

## 蓝图用法

根据提供的源码，`WebAPIOpenAPI` 模块主要负责解析和转换逻辑，其核心类（如 `FWebAPIOpenAPISchemaConverter` 和 `FWebAPISwaggerSchemaConverter`）通常不直接暴露为蓝图节点。蓝图资产的生成可能由 `WebAPIEditor` 或 `WebAPIBlueprintGraph` 模块处理。此处描述的用法主要面向代码生成和 C++ 使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图可调用函数） | 此模块主要提供后端解析和转换功能，通常不直接在蓝图中使用。生成的蓝图资产可能包含对应的节点。 | `FWebAPIOpenAPISchemaConverter` |

### 使用示例（蓝图描述）

蓝图层面，此插件更侧重于提供一个编辑器工具或向导，引导用户导入规范文件并生成对应的蓝图资产。具体的蓝图用法需参考生成后的 `WebAPIBlueprintGraph` 模块所提供的蓝图节点。

## C++ 用法

重点在于利用提供的转换器将 OpenAPI/Swagger 规范数据结构转换为 UE 的 WebAPI 数据结构。

### 头文件引入

```cpp
// 对于 OpenAPI 3.0 (V3)
#include "V3/WebAPIOpenAPIProvider.h"
#include "V3/WebAPIOpenAPISchema.h"
#include "V3/WebAPIOpenAPIConverter.h"

// 对于 Swagger 2.0 (V2)
#include "V2/WebAPISwaggerProvider.h"
#include "V2/WebAPISwaggerSchema.h"
#include "V2/WebAPISwaggerConverter.h"
```

### 基本用法

以下示例展示了如何使用 `FWebAPIOpenAPIProvider` 将一个 OpenAPI 3.0 JSON 字符串转换为 UE 的 `UWebAPISchema` 对象。

```cpp
// 假设已获取到 JSON 字符串 OpenAPIJsonString
FString OpenAPIJsonString = TEXT("{ \"openapi\": \"3.0.0\", ... }");
TWeakObjectPtr<UWebAPIDefinition> Definition = /* 你的 UWebAPIDefinition 对象 */;

// 创建并使用 OpenAPI Provider
FWebAPIOpenAPIProvider OpenAPIProvider;
TFuture<EWebAPIConversionResult> ResultFuture = OpenAPIProvider.ConvertToWebAPISchema(Definition);

// 处理异步结果
ResultFuture.Then([](TFuture<EWebAPIConversionResult> Result)
{
    if (Result.Get() == EWebAPIConversionResult::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("OpenAPI Schema conversion succeeded."));
        // UWebAPISchema 现在已在 Definition 对象中填充
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("OpenAPI Schema conversion failed."));
    }
});
```

### 进阶用法

直接使用转换器类 `FWebAPIOpenAPISchemaConverter` 可以获得更多控制。首先需要解析 JSON 为 `UE::WebAPI::OpenAPI::V3::FOpenAPIObject` 结构体。

```cpp
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "V3/WebAPIOpenAPISchema.h"
#include "V3/WebAPIOpenAPIConverter.h"

// 1. 解析 JSON 到 FOpenAPIObject
FString JsonString = TEXT("{ \"openapi\": \"3.0.0\", ... }");
TSharedRef<FJsonObject> JsonObject = MakeShareable(new FJsonObject());
TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);

if (FJsonSerializer::Deserialize(Reader, JsonObject))
{
    UE::WebAPI::OpenAPI::V3::FOpenAPIObject OpenAPIDoc;
    if (OpenAPIDoc.FromJson(JsonObject))
    {
        // 2. 创建消息日志和设置
        TSharedRef<FWebAPIMessageLog> MessageLog = MakeShared<FWebAPIMessageLog>();
        FWebAPIProviderSettings Settings; // 根据需要配置

        // 3. 创建目标 UWebAPISchema
        UWebAPISchema* Schema = NewObject<UWebAPISchema>();

        // 4. 创建转换器并执行转换
        UE::WebAPI::OpenAPI::FWebAPIOpenAPISchemaConverter Converter(
            MakeShareable(new UE::WebAPI::OpenAPI::V3::FOpenAPIObject(OpenAPIDoc)),
            Schema,
            MessageLog,
            Settings
        );

        if (Converter.Convert())
        {
            UE_LOG(LogTemp, Log, TEXT("Direct conversion succeeded. Schema has %d services."), Schema->GetServices().Num());
            // 现在可以使用 Schema 对象，例如遍历其中的 Services 和 Operations
        }
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何将一个简单的 OpenAPI 3.0 JSON 解析为 `UWebAPISchema`。

**WebAPIDemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "WebAPIDefinition.h" // 假设 UWebAPIDefinition 在此头文件
#include "WebAPIDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UWebAPIDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UWebAPIDemoComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "WebAPI Demo")
    void ImportAndConvertOpenAPI(const FString& JsonString);

    UPROPERTY(BlueprintReadOnly, Category = "WebAPI Demo")
    TObjectPtr<UWebAPIDefinition> APIDefinition;
};
```

**WebAPIDemoComponent.cpp**
```cpp
#include "WebAPIDemoComponent.h"
#include "V3/WebAPIOpenAPIProvider.h"
#include "V3/WebAPIOpenAPISchema.h"
#include "V3/WebAPIOpenAPIConverter.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

UWebAPIDemoComponent::UWebAPIDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    APIDefinition = CreateDefaultSubobject<UWebAPIDefinition>(TEXT("APIDefinition"));
}

void UWebAPIDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    // 示例 OpenAPI 3.0 JSON (简化版)
    FString SimpleJson = TEXT(R"({
        "openapi": "3.0.0",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        },
        "paths": {
            "/pets": {
                "get": {
                    "summary": "List all pets",
                    "operationId": "listPets",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": false,
                            "schema": {
                                "type": "integer",
                                "format": "int32"
                            }
                        }
                    ]
                }
            }
        }
    })");

    ImportAndConvertOpenAPI(SimpleJson);
}

void UWebAPIDemoComponent::ImportAndConvertOpenAPI(const FString& JsonString)
{
    if (!APIDefinition)
    {
        UE_LOG(LogTemp, Error, TEXT("APIDefinition is null."));
        return;
    }

    // 使用 Provider 异步转换
    FWebAPIOpenAPIProvider Provider;
    TFuture<EWebAPIConversionResult> Future = Provider.ConvertToWebAPISchema(APIDefinition);

    // 注意：在实际异步操作中，需要处理 Future。这里为了演示，假设 Provider 内部会利用 InDefinition 设置数据。
    // 一个更直接的方式是像“进阶用法”中那样直接使用转换器。
    // 这里我们直接使用转换器来演示同步流程。

    TSharedRef<FJsonObject> JsonObject = MakeShareable(new FJsonObject());
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);

    if (FJsonSerializer::Deserialize(Reader, JsonObject))
    {
        UE::WebAPI::OpenAPI::V3::FOpenAPIObject OpenAPIDoc;
        if (OpenAPIDoc.FromJson(JsonObject))
        {
            TSharedRef<FWebAPIMessageLog> MessageLog = MakeShared<FWebAPIMessageLog>();
            FWebAPIProviderSettings Settings;
            UWebAPISchema* Schema = APIDefinition->GetOrCreateSchema();

            UE::WebAPI::OpenAPI::FWebAPIOpenAPISchemaConverter Converter(
                MakeShareable(new UE::WebAPI::OpenAPI::V3::FOpenAPIObject(OpenAPIDoc)),
                Schema,
                MessageLog,
                Settings
            );

            if (Converter.Convert())
            {
                UE_LOG(LogTemp, Log, TEXT("Demo: Converted OpenAPI schema with %d services."), Schema->GetServices().Num());
                // 可以在这里检查生成的 Service (对应 "/pets" 路径) 和 Operation (对应 GET 请求)
            }
        }
    }
}
```

## 模块依赖

从模块名称和功能推断，使用者可能需要依赖以下模块。请根据实际情况在 `Build.cs` 中添加。

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心的 WebAPI 数据模型和基础框架 |
| `WebAPIOpenAPI` | OpenAPI/Swagger 规范解析与转换 |
| `Json` | 解析 JSON 字符串 |
| `JsonUtilities` | JSON 与 UObject 之间的转换工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量隐式转换为单精度浮点数可能产生的警告。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString，可能涉及内存或性能优化。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，可能涉及日志系统的更新或标准化。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复，以释放内存。这是一个内存优化。 |
| 2026-02-18 | `516817d0` | PR #13954: fix(deps): on-headers is vulnerable to http response header manipulation (and other vulne | 修复了 on-headers 依赖项存在的 HTTP 响应头操纵等安全漏洞。 |

### 维护评价

`WebAPI` 是一个**实验性**插件，创建于约 4 年前（2022年7月）。从 git 历史看，它在 2026 年仍有持续的维护和更新，包括代码重构、性能优化、安全漏洞修复和编译警告修复。这表明该插件**仍在维护中**，但因其“实验性”状态，可能尚未达到生产就绪的稳定程度，API 或生成代码的结构在未来版本中可能会发生变化。

**推荐**：如果你的项目需要快速集成 OpenAPI/Swagger 规范的 Web 服务，并且可以接受实验性插件的潜在风险，可以尝试使用此插件来提升开发效率。建议密切关注 Epic Games 的更新日志和此插件的变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Web/WebAPI)
- [官方文档]()（无）
- [测试用例]()（需在 `Engine/Tests/` 或插件内部查找）