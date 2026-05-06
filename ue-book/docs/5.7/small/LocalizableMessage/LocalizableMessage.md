# Localizable Message

> Utility for a text message that can be replicated. It supports parameter resolution for the client.

| 属性 | 值 |
|---|---|
| 中文名 | 本地化消息 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LocalizableMessage` (Runtime), `LocalizableMessageBlueprint` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LocalizableMessage) | |

## 用途

该插件提供了一种**可网络复制**的文本消息结构 `FLocalizableMessage`，并支持在客户端按当前语言和上下文解析参数，最终生成本地化后的 `FText`。核心设计如下：

- 服务器发送一个只包含 **Key**（本地化键）、**DefaultText**（回退文本）和 **Substitutions**（参数数组）的结构。
- 客户端通过 `FLocalizableMessageProcessor` 将 Key 解析为本地化文本，并将参数类型映射到 `FFormatArgumentValue`，完成文本格式化。
- 参数类型可通过 `RegisterLocalizableType` 模板方法注册任意引擎结构（如 int、float、string、甚至嵌套的 `FLocalizableMessage`），实现高度自定义。

该插件解决的是**多语言环境中带参数文本的复制与本地化**问题，适用于多人游戏、UI 消息、HUD 提示等需要网络同步文本的场景。

## 使用场景

- **击杀公告**：服务器广播“{PlayerA} killed {PlayerB}”，客户端根据语言将 `{PlayerA}`、`{PlayerB}` 替换为玩家名称并按照本地语法顺序呈现。
- **技能描述**：服务器发送“技能 {SkillName} 冷却剩余 {Cooldown} 秒”，客户端自动处理数字格式和小数点。
- **系统消息**：如“获得 {Count} 金币”，客户端根据语言替换数字并处理复数规则。

## 蓝图用法

> 注意：`FLocalizableMessage` 标记为 `BlueprintType`，但核心处理逻辑 `FLocalizableMessageProcessor` 仅在 C++ 中可用。蓝图通常需要结合 LocalizableMessageBlueprint（未提供源码）或自定义封装。

### 核心类型

| 结构体 | 说明 | 所在头文件 |
|---|---|---|
| `FLocalizableMessage` | 可复制的消息结构，包含 Key、DefaultText、Substitutions | LocalizableMessage.h |
| `FLocalizableMessageParameterEntry` | 单个参数条目，包含 Key 和 FInstancedStruct Value | LocalizableMessage.h |
| `FLocalizableMessageParameterInt` | int64 参数包装 | LocalizableMessageBaseParameters.h |
| `FLocalizableMessageParameterFloat` | double 参数包装 | LocalizableMessageBaseParameters.h |
| `FLocalizableMessageParameterString` | FString 参数包装 | LocalizableMessageBaseParameters.h |
| `FLocalizableMessageParameterMessage` | 嵌套的 FLocalizableMessage 参数包装（用于组合） | LocalizableMessageBaseParameters.h |

### 蓝图节点

当前模块未导出任何蓝图可调用函数，但蓝图可以直接创建 `FLocalizableMessage` 变量并设置属性（如 `Key`、`DefaultText`）。参数数组需要 C++ 填充。若需要蓝图调用本地化转换，建议使用 `LocalizableMessageBlueprint` 模块（若有提供 `MakeLiteralMessage` 或 `LocalizeMessage` 节点）。

## C++ 用法

### 头文件引入

```cpp
#include "LocalizableMessage.h"
#include "LocalizableMessageProcessor.h"
#include "LocalizableMessageBaseParameters.h"
#include "LocalizationContext.h"
```

### 基本用法

**1. 构造并本地化一个消息**

从 [测试用例 / Engine/Source/Programs/HeadlessChaos/Private/HeadlessChaosTestLocalizableMessage.cpp] 提取（示例路径，实际测试不在插件内）。

```cpp
// 1. 构造消息
FLocalizableMessage Message;
Message.Key = TEXT("KillMessage");           // 本地化表中的键
Message.DefaultText = FText::FromString(TEXT("{0} killed {1}")); // 回退文本

// 2. 设置参数（int 和 string）
FLocalizableMessageParameterInt ParamA;
ParamA.Value = 10;

FLocalizableMessageParameterString ParamB;
ParamB.Value = TEXT("PlayerTwo");

FLocalizableMessageParameterEntry Entry1(TEXT("Count"), FInstancedStruct::Make(ParamA));
FLocalizableMessageParameterEntry Entry2(TEXT("Name"), FInstancedStruct::Make(ParamB));
Message.Substitutions = { Entry1, Entry2 };

// 3. 获取 Processor 并本地化
ILocalizableMessageModule& Module = ILocalizableMessageModule::Get();
FLocalizableMessageProcessor& Processor = Module.GetLocalizableMessageProcessor();

FLocalizationContext Context; // 可传入 WorldContext 和语言覆盖
FText LocalizedText = Processor.Localize(Message, Context);
```

**2. 注册自定义参数类型**

```cpp
// 假设我们有一个自定义结构 FItemInfo
USTRUCT()
struct FItemInfo
{
    GENERATED_BODY()
    UPROPERTY() FString ItemName;
    UPROPERTY() int32 Count;
};

// 在模块启动时注册
void RegisterCustomTypes()
{
    FLocalizableMessageProcessor& Processor = ILocalizableMessageModule::Get().GetLocalizableMessageProcessor();

    // 使用 ScopedRegistrations 确保生命周期
    FLocalizableMessageProcessor::FScopedRegistrations Registrations;

    Processor.RegisterLocalizableType<FItemInfo>(
        [](const FItemInfo& ItemInfo, const FLocalizationContext&) -> FFormatArgumentValue
        {
            // 将自定义类型转换为 FText 或数字等
            FText Formatted = FText::Format(NSLOCTEXT("Game", "ItemFormat", "{0}x {1}"), ItemInfo.Count, FText::FromString(ItemInfo.ItemName));
            return FFormatArgumentValue(Formatted);
        },
        Registrations
    );

    // 注意：Registrations 是作用域对象，离开作用域后自动注销。也可手动调用 UnregisterLocalizableTypes。
}
```

### 进阶用法

**1. 嵌套消息** （使用 `FLocalizableMessageParameterMessage`）

```cpp
FLocalizableMessage InnerMessage;
InnerMessage.Key = TEXT("PlayerNameKey");
InnerMessage.DefaultText = FText::FromString(TEXT("Unknown"));

FLocalizableMessageParameterMessage Param;
Param.Value = InnerMessage;

FLocalizableMessage OuterMessage;
OuterMessage.Key = TEXT("WelcomeMessage");
OuterMessage.Substitutions = { FLocalizableMessageParameterEntry(TEXT("Player"), FInstancedStruct::Make(Param)) };

// 本地化时，处理器会递归解析 InnerMessage
FText Result = Processor.Localize(OuterMessage, Context);
```

**2. 使用本地化键互转工具**

```cpp
FTextId MyTextId = FText::GetEmpty().GetSourceString().GetTextId(); // 示例
FString MessageKey;
if (UE::LocalizableMessageTextInterop::TextIdToMessageKey(MyTextId, MessageKey))
{
    // 将 FText 的标识符转换为 FLocalizableMessage 可用的 Key
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何创建消息并注册参数类型。

**MyGameModule.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FLocalizableMessageProcessor::FScopedRegistrations Registrations;
};
```

**MyGameModule.cpp**

```cpp
#include "MyGameModule.h"
#include "LocalizableMessage.h"
#include "LocalizableMessageProcessor.h"
#include "LocalizableMessageBaseParameters.h"
#include "LocalizationContext.h"
#include "ILocalizableMessageModule.h"

void FMyGameModule::StartupModule()
{
    // 注册 int64 参数类型（系统已默认注册？为了演示，显式注册）
    // 注意：实际上 base types 可能已被 LocalizableMessageBlueprint 注册，这里仅为演示
    FLocalizableMessageProcessor& Processor = ILocalizableMessageModule::Get().GetLocalizableMessageProcessor();

    Processor.RegisterLocalizableType<FLocalizableMessageParameterInt>(
        [](const FLocalizableMessageParameterInt& Value, const FLocalizationContext&) -> FFormatArgumentValue
        {
            return FFormatArgumentValue(Value.Value);
        },
        Registrations
    );

    Processor.RegisterLocalizableType<FLocalizableMessageParameterString>(
        [](const FLocalizableMessageParameterString& Value, const FLocalizationContext&) -> FFormatArgumentValue
        {
            return FFormatArgumentValue(FText::FromString(Value.Value));
        },
        Registrations
    );

    // 使用示例
    FLocalizableMessage Message;
    Message.Key = TEXT("Greeting");
    Message.DefaultText = FText::FromString(TEXT("Hello {Name}!"));

    FLocalizableMessageParameterString Param;
    Param.Value = TEXT("World");

    Message.Substitutions.Add(FLocalizableMessageParameterEntry(TEXT("Name"), FInstancedStruct::Make(Param)));

    FLocalizationContext Context;
    FText Localized = Processor.Localize(Message, Context);
    UE_LOG(LogTemp, Log, TEXT("Localized: %s"), *Localized.ToString());
}

void FMyGameModule::ShutdownModule()
{
    // Registrations 析构时自动注销，不需要手动调用
}
```

## 模块依赖

根据 `Build.cs` 和代码引用，本模块依赖如下（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `StructUtils` | 提供 `FInstancedStruct`，用于存储任意参数类型 |

> 注意：`LocalizableMessageBlueprint` 模块可能额外依赖 `BlueprintGraph` 等，但本模块无需。

## 维护状态

### 近期更新

从 git log 获取最近 5 次 commit（截至 2025-08-12）：

- 2025-08-12 `f3d05004` 允许在蓝图中比较 HUD 消息（`Made it so that Hud messages could be compared in Blueprints.`）
- 2025-06-26 `a2e75189` 为所有具有 `.gen.cpp` 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`
- 2025-04-23 `6ae57335` 使用 UnrealGame 构建目标将所有文件转换为方法/静态变量添加 `dllstorage`
- 2024-12-06 `3b9c9c2a` 添加 Verse 消息辅助函数，将 `verse::message` 转换为 `FText`
- 2024-11-13 `e84e906f` 修复 `FTextHistory` 以支持事务（初始版本改进）

### 维护评价

- **创建时间**：2024-11-13，至今约 1 年，属于较新插件。
- **最近更新**：最近 3 个月内有功能更新（2025-08-12 的蓝图比较支持），表明仍在活跃维护。
- **更新内容**：包括功能增强、编译适配、跨模块集成（Verse）。
- **已知问题**：未发现明显废弃标记或已知限制。
- **推荐使用**：✅ 推荐。该插件专为网络复制文本本地化设计，用法清晰，扩展性良好。适合需要多语言多人在线的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LocalizableMessage)
- [官方文档]（暂无，建议参阅引擎内部测试用例）
- [测试用例]（推测位于 `Engine/Source/Programs/HeadlessChaos/Private/HeadlessChaosTestLocalizableMessage.cpp`，但未在插件目录内）