# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UMG 控件） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensUncookedOnly` (UncookedOnly), `NamingTokensUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/NamingTokens) | |

## 用途

NamingTokens 是一个通用的**模板字符串求值系统**，允许开发者定义可识别的 token（标记），并在字符串中将其解析替换为实际值。

想象一下你在做 Virtual Production 工作：Take Recorder 需要自动命名录制文件，Cinematic Assembly Tools 需要按规则生成序列名称，Performance Capture 需要标记每次表演的数据。这些工具都需要一套「在字符串里放占位符，运行时自动替换」的机制。NamingTokens 就是这个通用基础设施。

核心设计思想：
- **命名空间隔离**：每个工具（或项目）有自己的 namespace，避免 token 名冲突
- **统一求值入口**：通过 `UNamingTokensEngineSubsystem` 一次调用即可解析包含多个命名空间 token 的复杂字符串
- **蓝图可扩展**：子类化 `UNamingTokens` 即可在蓝图中定义自定义 token
- **UMG 集成**：提供 `UNamingTokensEditableText` 控件，用户可在 UI 中编辑含 token 的模板并实时预览解析结果

## 使用场景

- **你正在开发 Take Recorder 工具** → 需要自动为录制文件命名（如 `Take_{take}_{date}`）→ 使用 NamingTokens 注册 `take`、`date` 等 token
- **你在做 Cinematic Assembly** → 需要按模板生成 Sequence 名称（如 `{scene}_{shot}_{version}`）→ 子类化 UNamingTokens 定义项目级 token
- **你需要在 UI 中让用户编辑模板字符串** → 使用 `UNamingTokensEditableText` UMG 控件，自带 token 语法高亮和自动补全下拉框
- **你有一个项目需要统一的命名规则** → 注册全局命名空间，用户写 `{project}` 就行，不需要 `{g:project}`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Naming Tokens` | 根据命名空间查找 NamingTokens 对象（支持原生+蓝图） | `UNamingTokensEngineSubsystem` |
| `Get Naming Tokens Native` | 根据命名空间查找原生 NamingTokens 对象 | `UNamingTokensEngineSubsystem` |
| `Get Multiple Naming Tokens` | 批量查找多个命名空间的 NamingTokens | `UNamingTokensEngineSubsystem` |
| `Evaluate Token Text` | 解析含 token 的 FText，返回求值结果 | `UNamingTokensEngineSubsystem` |
| `Evaluate Token String` | 解析含 token 的 FString，返回求值结果 | `UNamingTokensEngineSubsystem` |
| `Evaluate Token List` | 批量求值一组 token 列表 | `UNamingTokensEngineSubsystem` |
| `Register Global Namespace` | 注册全局命名空间（token 无需加命名空间前缀） | `UNamingTokensEngineSubsystem` |
| `Unregister Global Namespace` | 取消全局命名空间注册 | `UNamingTokensEngineSubsystem` |
| `Is Global Namespace Registered` | 检查命名空间是否已注册为全局 | `UNamingTokensEngineSubsystem` |
| `Get Global Namespaces` | 获取所有已注册的全局命名空间 | `UNamingTokensEngineSubsystem` |
| `Get All Namespaces` | 发现项目中所有命名空间（原生+蓝图） | `UNamingTokensEngineSubsystem` |
| `Clear Cached Naming Tokens` | 清除缓存（修改 BP 资产后调用） | `UNamingTokensEngineSubsystem` |

### 使用示例（蓝图描述）

**快速求值示例**：

1. 获取 Engine Subsystem → `Get Engine Subsystem` 选择 `NamingTokensEngineSubsystem`
2. 连接到 `Evaluate Token String` 节点
3. 输入字符串：`"MyProject_Take_{take}"`
4. Filter Args 中设置 `AdditionalNamespacesToInclude` 为 `["takerecorder"]`
5. 输出的 `EvaluatedText` 即为 `"MyProject_Take_001"` 之类的解析结果

**注册全局命名空间示例**：

1. `Get Engine Subsystem` → `NamingTokensEngineSubsystem`
2. `Register Global Namespace`，输入 `"g"`
3. 之后所有求值调用中，`{project}` 等全局 token 无需写 `{g:project}` 即可生效

**自定义命名 Token（蓝图子类）**：

1. 新建蓝图类，父类选择 `UNamingTokens`
2. 在 Class Defaults 中设置 `Namespace` 为 `"mytools"`
3. 在 `CustomTokens` 数组中添加 token：`TokenKey = "shot"`，`DisplayName = "Shot Number"`
4. 为每个 token 的 `FunctionName` 指定一个蓝图函数（返回 `FText`）
5. 之后就可以在字符串中使用 `{mytools:shot}` 或注册全局后使用 `{shot}`

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokens.h"
#include "NamingTokensEngineSubsystem.h"
#include "NamingTokenData.h"
#include "NamingTokensEvaluationData.h"
```

### 基本用法

**创建自定义命名空间（C++ 子类）**

源码参考：`TakeRecorderNamingTokens.h/cpp`、`GlobalNamingTokens.h/cpp`

```cpp
// MyNamingTokens.h
#pragma once
#include "NamingTokens.h"
#include "MyNamingTokens.generated.h"

UCLASS(NotBlueprintable)
class UMyNamingTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyNamingTokens()
    {
        Namespace = TEXT("myproject");
    }

protected:
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override
    {
        // 添加一个自定义 token
        Tokens.Add(FNamingTokenData(
            TEXT("level"),
            LOCTEXT("LevelName", "Level Name"),
            FNamingTokenData::FTokenProcessorDelegateNative::CreateLambda([]() -> FText
            {
                return FText::FromString(TEXT("TestLevel"));
            })
        ));
    }
};
```

**通过 Subsystem 求值字符串**

```cpp
// 获取 subsystem
UNamingTokensEngineSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();

// 方式一：直接求值（自动发现所有命名空间）
FNamingTokenFilterArgs Filter;
Filter.bIncludeGlobal = true;  // 包含全局命名空间（如 "g"）
FNamingTokenResultData Result = Subsystem->EvaluateTokenString(
    TEXT("Take_{take}_on_{date}"), Filter);

// Result.EvaluatedText 即为替换后的完整字符串
// Result.TokenValues 包含每个 token 的求值详情

// 方式二：指定命名空间求值
UNamingTokens* MyTokens = Subsystem->GetNamingTokens(TEXT("myproject"));
if (MyTokens)
{
    FNamingTokenResultData Result = MyTokens->EvaluateTokenText(
        FText::FromString(TEXT("{level}")));
    // Result.EvaluatedText == "TestLevel"
}
```

来源：`NamingTokensEngineSubsystem.cpp`、`NamingTokens.cpp`

### 进阶用法

**注册全局命名空间**

```cpp
// 注册后，"myproject" 命名空间的 token 无需 "myproject:" 前缀
Subsystem->RegisterGlobalNamespace(TEXT("myproject"));
// 之后 {level} 就能直接解析，不需要 {myproject:level}
```

**使用 Context 对象传递额外数据**

```cpp
// Context 允许你在求值时传递任意 UObject，token 处理函数可以读取
UObject* MyContext = GetMyContextObject();
FNamingTokenFilterArgs Filter;
TArray<UObject*> Contexts = { MyContext };
FNamingTokenResultData Result = Subsystem->EvaluateTokenString(
    TEXT("{take}"), Filter, Contexts);
```

来源：TakeRecorder 的 `UTakeRecorderNamingTokens` 就通过 Context 获取 `UTakeMetaData`

**External Tokens（临时外部 token 注册）**

```cpp
// 在某些场景下，你可能需要临时注入 token，而不是定义为永久的 class
UNamingTokens* Tokens = Subsystem->GetNamingTokens(TEXT("myproject"));
FGuid ExternalGuid;
TArray<FNamingTokenData>& ExtTokens = Tokens->RegisterExternalTokens(ExternalGuid);
ExtTokens.Add(FNamingTokenData(
    TEXT("temp_value"),
    LOCTEXT("TempValue", "Temporary Value"),
    FNamingTokenData::FTokenProcessorDelegateNative::CreateLambda([]() -> FText
    {
        return FText::FromString(TEXT("RuntimeValue"));
    })
));

// 使用完毕后清理
Tokens->UnregisterExternalTokens(ExternalGuid);
```

**命名空间过滤器**

```cpp
// 注册过滤器，限制可用的命名空间
Subsystem->RegisterNamespaceFilter(FName("MyFilter"),
    FFilterNamespace::CreateLambda([](TSet<FString>& Namespaces)
    {
        // 只允许使用 "g" 和 "myproject" 命名空间
        Namespaces = { TEXT("g"), TEXT("myproject") };
    }));
```

## Demo 示例

### 最小可用示例

```cpp
// MyNamingTokensSubsystem.h
#pragma once
#include "NamingTokens.h"
#include "MyNamingTokensSubsystem.generated.h"

UCLASS()
class UMyNamingTokensSubsystem : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyNamingTokensSubsystem()
    {
        Namespace = TEXT("demo");
    }

protected:
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override
    {
        Tokens.Add(FNamingTokenData(
            TEXT("greeting"),
            LOCTEXT("Greeting", "Greeting Message"),
            FNamingTokenData::FTokenProcessorDelegateNative::CreateLambda([]() -> FText
            {
                return FText::FromString(TEXT("Hello World"));
            })
        ));
    }
};
```

```cpp
// 调用处
#include "NamingTokensEngineSubsystem.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    auto* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();
    Subsystem->RegisterGlobalNamespace(TEXT("demo"));

    FNamingTokenResultData Result = Subsystem->EvaluateTokenString(
        TEXT("Message: {greeting}"));

    UE_LOG(LogTemp, Log, TEXT("Result: %s"), *Result.EvaluatedText.ToString());
    // 输出: "Message: Hello World"
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "NamingTokens" });
```

## 内置全局 Token

NamingTokens 自带一个全局命名空间 `g`（`UGlobalNamingTokens`），提供以下内置 token：

| Token | 说明 | 示例输出 |
|---|---|---|
| `{g:project}` / `{project}` | 项目名称 | `MyProject` |
| `{g:user}` / `{user}` | 会话所有者 | `username` |
| `{g:yyyy}` / `{yyyy}` | 四位年份 | `2025` |
| `{g:yy}` / `{yy}` | 两位年份 | `25` |
| `{g:Mmm}` / `{Mmm}` | 3字符月份（Pascal Case） | `Jan` |
| `{g:MMM}` / `{MMM}` | 3字符月份（大写） | `JAN` |
| `{g:mmm}` / `{mmm}` | 3字符月份（小写） | `jan` |
| `{g:mm}` / `{mm}` | 两位月份 | `01` |
| `{g:Ddd}` / `{Ddd}` | 3字符星期（Pascal Case） | `Mon` |
| `{g:DDD}` / `{DDD}` | 3字符星期（大写） | `MON` |
| `{g:ddd}` / `{ddd}` | 3字符星期（小写） | `mon` |
| `{g:dd}` / `{dd}` | 两位日期 | `05` |
| `{g:ampm}` / `{ampm}` | am/pm（小写） | `pm` |
| `{g:AMPM}` / `{AMPM}` | AM/PM（大写） | `PM` |
| `{g:12h}` / `{12h}` | 12小时制小时 | `02` |
| `{g:24h}` / `{24h}` | 24小时制小时 | `14` |
| `{g:min}` / `{min}` | 分钟 | `30` |
| `{g:sec}` / `{sec}` | 秒 | `45` |
| `{g:ms}` / `{ms}` | 毫秒 | `123` |

> 注册全局命名空间后，无需 `{g:}` 前缀，直接写 `{project}` 即可。

## UMG 控件

NamingTokens 提供了一个 UMG 控件 `UNamingTokensEditableText`（继承自 `UMultiLineEditableText`），用于在 UI 中编辑带 token 的模板字符串。

### 核心特性

- **语法高亮**：token 自动高亮显示
- **实时预览**：失焦时显示解析后的结果文本
- **自动补全下拉框**：输入 `{` 时弹出可用 token 列表
- **Token 图标**：可选显示 token 图标
- **错误提示**：可选显示 token 格式错误

### 蓝图属性

| 属性 | 说明 |
|---|---|
| `FilterArgs` | 命名空间过滤参数 |
| `Contexts` | 求值时的上下文对象数组 |
| `bEnableSuggestionDropdown` | 是否启用下拉建议框 |
| `bDisplayTokenIcon` | 是否显示 token 图标 |
| `bDisplayErrorMessage` | 是否显示错误信息 |
| `bDisplayBorderImage` | 是否显示边框 |
| `bCanDisplayResolvedText` | 是否允许显示解析后的文本 |
| `ArgumentStyle` | token 参数的文本样式 |

### 蓝图方法

| 方法 | 说明 |
|---|---|
| `GetResolvedText` | 获取解析后的文本 |
| `GetTokenizedText` | 获取原始 token 文本 |
| `SetContexts` | 设置求值上下文 |
| `OnPreEvaluateNamingTokens` | 求值前的事件委托 |

## Token 语法规范

- **Token 格式**：`{tokenkey}` 或 `{namespace:tokenkey}`
- **命名空间分隔符**：`:`（冒号）
- **合法字符**：Token key 和 namespace 只能包含字母、数字和下划线 `_`
- **大小写**：默认大小写不敏感，可通过 `FNamingTokenFilterArgs::bForceCaseSensitive` 强制敏感
- **全局命名空间**：注册为全局后，无需 `namespace:` 前缀

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、字符串操作 |
| `Engine` | UEngineSubsystem、UWorld 访问 |
| `CoreUObject` | UObject 反射系统 |
| `NamingTokens` | 核心 Runtime 模块（其他模块依赖此模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-10-03 | `c39e0cbd` | 将 UMG 控件显示名改为 "Naming Tokens Editable Text Box"，与 C++ 类名和通用命名保持一致 |
| 2025-10-02 | `b6f28f77` | 修复文档字符串 |
| 2025-10-02 | `16e0e9a8` | Slate Widget: Contexts 和 FilterArgs 参数改为按值传递，EvaluateNamingTokens 方法改为 public |

### 维护评价

- **创建时间**：2025-01-13，约 1 年前，非常年轻的插件
- **实验性标记**：`IsExperimentalVersion = true`，说明 Epic 仍在迭代此功能
- **维护活跃**：最近更新在 2025-10 月，有功能调整和文档修复，属于活跃维护
- **使用者众多**：Take Recorder、Cinematic Assembly Tools、Performance Capture Workflow 等多个 VP 工具依赖此插件
- **推荐使用**：⚠️ 谨慎使用。虽然功能完整，但实验性标记意味着 API 可能在未来版本中发生变化。如果你的项目在 Virtual Production 领域，建议关注此插件的后续演进

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/NamingTokens)
- 官方文档：无
- 使用者示例：
  - [TakeRecorderNamingTokens](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderNamingTokens)
  - [CineAssemblyNamingTokens](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CinematicAssemblyTools/Source/CineAssemblyTools/Public/CineAssemblyNamingTokens.h)
  - [PCapNamingTokens](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow/Source/PerformanceCaptureWorkflow/Private/PCapNamingTokens.h)
