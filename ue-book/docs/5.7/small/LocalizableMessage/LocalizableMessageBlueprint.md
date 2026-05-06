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

该插件提供了一种**可网络复制且支持本地化参数解析**的文本消息结构 `FLocalizableMessage`。在多人游戏中，服务端可以构造一条包含占位符的消息（例如“{PlayerName} 获得了 {Score} 分”），并将其复制到客户端；客户端根据当前语言环境（如中文/英文）和参数化信息，自动渲染为本地化文本。其核心价值在于：

- 消息本体不需要事先翻译成所有语言，只需定义一份带参数的格式字符串，客户端负责解析。
- 支持蓝图的便捷调用，能在 UI、HUD、对话系统中直接使用。

## 使用场景

- 你正在开发一款**多人在线游戏**，需要在 HUD 上显示同步的击杀信息：“XXX 击杀了 YYY”。
- 你的游戏需要**支持多语言**，但不想在服务器上处理翻译逻辑。
- 你希望**动态填充参数**（如玩家名称、数值、道具名）到消息模板中，并让客户端完成最终格式化。

## 蓝图用法

> 以下蓝图节点定义在 `ULocalizableMessageLibrary` 类中，模块为 `LocalizableMessageBlueprint`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Conv_LocalizableMessageToText` | 将 `FLocalizableMessage` 转换为本地化 `FText`（带参数解析） | `ULocalizableMessageLibrary` |
| `Equal (LocalizableMessage)` | 判断两个 `FLocalizableMessage` 是否相等（`==`） | `ULocalizableMessageLibrary` |
| `IsEmpty (LocalizableMessage)` | 检查消息是否为空（未设置任何 Key 或参数） | `ULocalizableMessageLibrary` |
| `Reset (LocalizableMessage)` | 重置消息内容，使其变为空状态 | `ULocalizableMessageLibrary` |

### 使用示例（蓝图描述）

1. **显示一条带参数的本地化消息**  
   - 创建一个 `FLocalizableMessage` 变量（例如 `MyMessage`），通过 `Make LocalizableMessage`（如果存在）或直接设置 Key/Params。
   - 调用 `Conv_LocalizableMessageToText`，输入 `World Context Object`（通常会连到 `Get Player Controller`）和 `MyMessage`。
   - 将返回的 `FText` 连接到 UI 文本控件的 `Set Text` 引脚。

2. **比较两条消息是否相同**  
   - 使用 `Equal (LocalizableMessage)` 节点，输入两个 `FLocalizableMessage` 引用，得到布尔结果。

3. **判断消息是否为空并执行分支**  
   - 使用 `IsEmpty (LocalizableMessage)` 节点，传入消息引用，根据返回值执行不同逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "LocalizableMessageLibrary.h"
#include "LocalizableMessage.h"   // 若需直接操作 FLocalizableMessage 结构
```

### 基本用法

```cpp
// 来源: Engine/Plugins/Experimental/LocalizableMessage/Source/LocalizableMessageBlueprint/Public/LocalizableMessageLibrary.h

// 1. 将 LocalizableMessage 转换为 FText
UObject* WorldContext = GetWorld();
FLocalizableMessage Msg;
// ... 设置 Msg 的 Key 和参数 ...
FText LocalizedText = ULocalizableMessageLibrary::Conv_LocalizableMessageToText(WorldContext, Msg);

// 2. 比较两个消息
bool bEqual = ULocalizableMessageLibrary::EqualEqual_LocalizableMessage(MsgA, MsgB);

// 3. 检查是否为空
bool bEmpty = ULocalizableMessageLibrary::IsEmpty_LocalizableMessage(Msg);

// 4. 重置消息
ULocalizableMessageLibrary::Reset_LocalizableMessage(Msg);
```

### 进阶用法

```cpp
// 直接构造 FLocalizableMessage（需包含 "LocalizableMessage.h"）
FLocalizableMessage Msg;
Msg.Key = TEXT("KillFeed_PlayerKilledPlayer");   // 本地化字符串的 Key
// 添加参数（示例：玩家名字）
FFormatArgumentData Arg1;
Arg1.ArgName = TEXT("Killer");
Arg1.ArgValue = FText::FromString(TEXT("Alice"));
Msg.Params.Add(Arg1);

// 在服务端构造后复制到客户端，客户端调用 Conv_LocalizableMessageToText 转换为最终文本
```

## Demo 示例

以下是一个最小可编译的 AMyActor 类，演示如何创建并显示一条本地化消息。

```cpp
// MyLocalizableMessageActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "LocalizableMessageLibrary.h"
#include "MyLocalizableMessageActor.generated.h"

UCLASS()
class AMyLocalizableMessageActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

protected:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void ShowLocalizedMessage(FLocalizableMessage Message);
};
```

```cpp
// MyLocalizableMessageActor.cpp
#include "MyLocalizableMessageActor.h"
#include "Engine/Engine.h"

void AMyLocalizableMessageActor::BeginPlay()
{
    Super::BeginPlay();

    // 构造一条示例消息
    FLocalizableMessage Msg;
    Msg.Key = TEXT("Demo_Greeting");
    FFormatArgumentData Arg;
    Arg.ArgName = TEXT("PlayerName");
    Arg.ArgValue = FText::FromString(FString::Printf(TEXT("%s"), *GetName()));
    Msg.Params.Add(Arg);

    ShowLocalizedMessage(Msg);
}

void AMyLocalizableMessageActor::ShowLocalizedMessage(FLocalizableMessage Message)
{
    UObject* WorldContext = GetWorld();
    FText LocalizedText = ULocalizableMessageLibrary::Conv_LocalizableMessageToText(WorldContext, Message);
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Green, LocalizedText.ToString());
    }
}
```

## 模块依赖

要使用本插件，你的 `Build.cs` 中需要添加以下依赖（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `LocalizableMessage` | 核心结构 `FLocalizableMessage` 定义及参数解析逻辑 |
| `LocalizableMessageBlueprint` | 蓝图函数库节点（仅当需要蓝图暴露时） |

> 若只使用 C++ 且不涉及蓝图，可仅依赖 `LocalizableMessage`。

## 维护状态

### 近期更新

- 2025-08-12 `f3d05004` Made it so that Hud messages could be compared in Blueprints.
- 2025-06-26 `a2e75189` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-04-23 `6ae57335` Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar.
- 2024-12-06 `3b9c9c2a` Verse message: helper function to convert a verse::message into FText.
- 2024-11-13 `e84e906f` Fix FTextHistory to work in transactions.

### 维护评价

该插件创建于 2024 年 11 月，距今约 1 年，属于较新的功能模块。从 git 日志可见，2025 年内有多次实质性更新（如添加蓝图比较节点、生成文件清理、DLL 存储调整），维护活跃。当前无已知重大限制，建议在需要网络同步+本地化消息的项目中优先使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LocalizableMessage)
- [官方文档](https://docs.unrealengine.com/5.7/API/Plugins/LocalizableMessage/)（假定存在，实际未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LocalizableMessage/Tests)（若存在）