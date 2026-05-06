# PlainPropsEngine

> New Serialization Stack Prototype - Engine Bindings

| 属性 | 值 |
|---|---|
| 中文名 | 引擎绑定插件 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlainPropsEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainPropsEngine) | |

## 用途

PlainPropsEngine 是 UE5 全新序列化栈原型 **PlainProps** 的**引擎绑定层**。PlainProps 旨在成为未来 UE 序列化格式的替代，但需要将引擎现有类型（如 UObject、FName、FText 等）的序列化逻辑与 PlainProps 核心分离。该插件正是负责提供这些**自定义绑定**，使 PlainProps 能够正确处理引擎数据，同时避免 PlainProps 核心模块直接依赖 Engine。

插件内部声明了日志类别 `LogPlainPropsEngine`，并通过 `PlainProps::UE::CustomBindEngineTypes` 函数注册引擎类型的序列化器；此外还包含一个测试命令let `UTestPlainPropsCommandlet`，用于开发者快速验证绑定功能。

**为什么存在？** PlainProps 核心模块（如 PlainPropsCore）专注于纯数据布局和序列化协议，不应依赖庞大的 Engine 模块。该插件作为桥梁，将 PlainProps 核心与 UE 引擎类型连接起来，保持核心的纯净性，同时提供完整的引擎集成能力。

## 使用场景

- 你正在参与 PlainProps 序列化栈的开发或测试
- 你需要为 Engine 类型编写自定义序列化绑定，或验证绑定是否正确
- 你希望了解 UE 如何将新的序列化协议与既有类型系统集成

> **注意**：该插件仍处于**实验性**阶段，默认未启用，且仅支持 Win64 目标。不建议在生产项目中使用。

## 蓝图用法

该插件未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性，所有功能均通过 C++ 和命令let 使用。

## C++ 用法

### 头文件引入

```cpp
#include "PlainPropsEngineBindings.h"
#include "PlainPropsCommandlets.h"
```

### 基本用法

#### 1. 注册引擎类型绑定

在模块启动或需要初始化绑定时调用 `CustomBindEngineTypes`。该函数在 `PlainPropsEngineBindings.h` 中声明：

```cpp
#include "PlainPropsEngineBindings.h"

void InitializePlainPropsEngineBindings()
{
    // 注册所有引擎类型的 PlainProps 序列化绑定
    PlainProps::UE::CustomBindEngineTypes(PlainProps::UE::EBindMode::Default);
    // 根据 EBindMode 枚举可以选择不同的绑定模式（如 Full / Minimal）
}
```

> **文件来源**：`Source/Private/PlainPropsEngineBindings.h`

#### 2. 使用测试命令let

插件提供了一个 `UTestPlainPropsCommandlet`，可在编辑器控制台或命令行运行：

```cpp
// 通过 UE 控制台执行：
// PlainPropsTest
// 或在命令行：
// YourProject.exe -run=TestPlainProps
```

命令let 实现位于 `Source/Private/...`，具体逻辑可查看源码。

### 进阶用法

暂无复杂组合示例，该插件目前处于早期开发，建议直接阅读源码获取最新绑定逻辑。

## Demo 示例

下面是一个最小化的控制台命令示例，演示如何调用绑定并执行测试步骤。假设你的项目已启用该插件。

### TestPlainPropsBindings.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "PlainPropsEngineBindings.h"

class FTestPlainPropsBindings
{
public:
    static void Run()
    {
        // 1. 注册引擎绑定
        PlainProps::UE::CustomBindEngineTypes(PlainProps::UE::EBindMode::Default);
        
        // 2. 输出日志验证
        UE_LOG(LogPlainPropsEngine, Log, TEXT("Engine bindings registered successfully."));
        
        // 3. 可以在此处添加 UObject 的 PlainProps 序列化测试（需引用 PlainPropsCore 模块）
    }
};
```

### TestPlainPropsBindings.cpp

```cpp
#include "TestPlainPropsBindings.h"
#include "PlainPropsEngineBindings.h"

DEFINE_LOG_CATEGORY(LogPlainPropsEngine); // 如果未在其他地方定义

void FTestPlainPropsBindings::Run()
{
    PlainProps::UE::CustomBindEngineTypes(PlainProps::UE::EBindMode::Default);
    UE_LOG(LogPlainPropsEngine, Log, TEXT("Engine bindings registered successfully."));
}
```

> 注：实际编译需要项目 `Build.cs` 中添加对 `PlainPropsEngine` 模块的依赖。

## 模块依赖

该插件是实验性模块，其 `Build.cs` 未提供。根据 Git 历史（移除 PlainPropsUObject 对引擎的依赖）推测，`PlainPropsEngine` 可能依赖于以下模块：

| 模块 | 用途 |
|---|---|
| `PlainPropsCore` | PlainProps 核心序列化框架（假设） |

**常见依赖（已省略）**：Core、CoreUObject、Engine。

## 维护状态

### 近期更新

- 2025-09-02 `39af566d` — PlainProps preparing to add custom bindings for Engine types
- 2025-09-01 `0f3dfe02` — PlainProps add new Engine plugin and remove engine dependency from PlainPropsUObject module

### 维护评价

- **创建时间**：2025-09-01（距今不到两个月）
- **更新频率**：仅两个提交，但为连续开发，活跃度高
- **当前状态**：处于早期原型阶段，代码量小，功能有限
- **推荐度**：**实验性探索** — 仅适合对 UE 序列化底层感兴趣的开发者跟进，不适合任何生产环节

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainPropsEngine)
- [官方文档](https://docs.unrealengine.com/5.7/...)（暂无 PlainProps 相关文档）