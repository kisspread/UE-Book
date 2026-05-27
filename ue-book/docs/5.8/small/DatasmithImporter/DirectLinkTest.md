# DirectLink Test

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | DirectLink 测试模块 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DirectLinkTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) | |

## 用途

**DirectLinkTest** 是 DatasmithImporter 插件中的一个**测试与演示模块**，而非核心生产功能。其主要用途是为 Unreal Engine 的 DirectLink 实时数据通信功能提供一个可控的蓝图和 C++ 测试环境。

DirectLink 是一种允许不同应用程序（如 3ds Max, Maya, Revit 与 Unreal Engine）之间进行实时场景数据同步的技术。`DirectLinkTest` 模块封装了建立发送方（Sender）和接收方（Receiver）端点、发送测试场景以及接收并打印场景内容等操作。开发者或技术美术可以使用它来快速验证 DirectLink 链路是否正常工作，排查通信问题，或者理解 DirectLink API 的基本使用流程。

## 使用场景

- 你正在集成 DirectLink 功能，并需要测试 Unreal Engine 作为数据接收方是否正常工作。
- 你需要测试 Unreal Engine 作为数据发送方，向其他支持 DirectLink 的应用程序推送场景数据。
- 你在开发或调试一个需要使用 DirectLink 的自定义数据管线，需要一个现成的测试工具来模拟场景传输。
- 你正在学习 DirectLink 的 API，需要一个简单的代码示例来参考。

## 蓝图用法

该模块通过 `UDirectLinkTestLibrary` 蓝图函数库暴露了所有功能，所有函数节点均位于“DirectLink”类别下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupSender` | 初始化发送方环境，为后续发送数据做准备。 | `UDirectLinkTestLibrary` |
| `StartSender` | 启动一个发送方端点，使其在网络上可见并准备发送。 | `UDirectLinkTestLibrary` |
| `SendScene` | 从指定文件路径加载一个 Datasmith 场景并通过已启动的发送方发送出去。 | `UDirectLinkTestLibrary` |
| `StopSender` | 停止并关闭发送方端点。 | `UDirectLinkTestLibrary` |
| `SetupReceiver` | 初始化接收方环境，为后续接收数据做准备。 | `UDirectLinkTestLibrary` |
| `StartReceiver` | 启动一个接收方端点，开始监听来自发送方的连接和数据。 | `UDirectLinkTestLibrary` |
| `StopReceiver` | 停止并关闭接收方端点。 | `UDirectLinkTestLibrary` |
| `DumpReceivedScene` | 将当前已接收到的场景内容以日志形式输出到 Output Log，用于验证接收结果。 | `UDirectLinkTestLibrary` |
| `TestParameters` | 一个参数化测试函数，具体测试内容需查看源码逻辑。 | `UDirectLinkTestLibrary` |
| `MakeEndpoint` | 创建一个新的 DirectLink 端点（通常是一个发送或接收通道），并返回其 ID。 | `UDirectLinkTestLibrary` |
| `DeleteEndpoint` | 通过 ID 删除一个之前创建的端点。 | `UDirectLinkTestLibrary` |
| `AddPublicSource` / `AddPublicDestination` | 将一个端点注册为公开的源或目的地，供其他应用程序发现。 | `UDirectLinkTestLibrary` |
| `DeleteAllEndpoint` | 删除所有通过此模块创建的端点。 | `UDirectLinkTestLibrary` |

### 使用示例（蓝图描述）

**发送数据测试流程**：
1. 创建一个 `SetupSender` 节点并连接其执行线到 `StartSender` 节点。
2. 连接 `StartSender` 的执行线到一个 `SendScene` 节点，并在 `InFilePath` 引脚上输入一个 `.udatasmith` 文件的路径。
3. 最后，将执行线连接到 `StopSender` 节点以清理资源。
4. 运行此蓝图，它将完成“初始化 -> 启动 -> 发送文件 -> 停止”的完整发送测试。

**接收数据测试流程**：
1. 创建一个 `SetupReceiver` 节点并连接其执行线到 `StartReceiver` 节点。
2. 保持 `StartReceiver` 节点的执行线开放（或连接到后续逻辑），此时引擎将在后台监听传入的连接。
3. 在另一个应用程序（如 Datasmith CAD Explorer）中使用 DirectLink 发送数据到本引擎。
4. 当你认为数据可能已到达时，可以触发 `DumpReceivedScene` 节点，检查 Output Log 中是否出现了接收到的场景对象信息。

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkTestLibrary.h"
```

### 基本用法

以下示例演示了如何在 C++ 中调用 `DirectLinkTest` 模块提供的静态函数，模拟一个简化的发送流程。这些函数本身就是静态的，可以直接调用。

```cpp
// 假设您想在一个自定义的编辑器工具按钮或自动化测试中执行DirectLink测试
// 需要在模块的 Build.cs 中添加对 DirectLinkTest 模块的依赖

#include "DirectLinkTestLibrary.h"

void RunDirectLinkSendTest(const FString& FilePath)
{
    // 1. 初始化发送环境
    if (UDirectLinkTestLibrary::SetupSender())
    {
        // 2. 启动发送端点
        if (UDirectLinkTestLibrary::StartSender())
        {
            // 3. 发送指定的场景文件
            bool bSuccess = UDirectLinkTestLibrary::SendScene(FilePath);
            UE_LOG(LogTemp, Log, TEXT("DirectLink SendScene for '%s' returned: %s"), *FilePath, bSuccess ? TEXT("Success") : TEXT("Fail"));

            // 4. 完成后停止发送端点
            UDirectLinkTestLibrary::StopSender();
        }
    }
}
```
*代码逻辑参考自 `DirectLinkTestLibrary.h` 中的函数声明。*

### 进阶用法

您也可以使用底层的端点管理函数来构建更灵活的测试，例如创建命名的端点并管理其生命周期。

```cpp
#include "DirectLinkTestLibrary.h"

void ManageDirectLinkEndpoints()
{
    // 创建一个名为 “MyTestSender” 的端点，开启详细日志
    int32 SenderEndpointId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("MyTestSender"), true);
    if (SenderEndpointId != -1)
    {
        // 为此端点注册一个公共的发送源，名称为 “SceneExport”
        UDirectLinkTestLibrary::AddPublicSource(SenderEndpointId, TEXT("SceneExport"));
        
        // ... 在此执行发送逻辑 ...

        // 测试结束后，可以按需删除端点
        UDirectLinkTestLibrary::DeleteEndpoint(SenderEndpointId);
    }

    // 或者一次性清理所有测试端点
    // UDirectLinkTestLibrary::DeleteAllEndpoint();
}
```

## Demo 示例

以下是一个可用于单元测试或简单控制台命令的 C++ 类，它封装了一个完整的发送-接收循环测试（顺序执行）。

**DirectLinkTestDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FDirectLinkTestDemo
{
public:
    /** 运行一个简单的端到端DirectLink通信测试。 */
    static bool RunSimpleTest(const FString& TestScenePath);
};
```

**DirectLinkTestDemo.cpp**
```cpp
#include "DirectLinkTestDemo.h"
#include "DirectLinkTestLibrary.h"

bool FDirectLinkTestDemo::RunSimpleTest(const FString& TestScenePath)
{
    UE_LOG(LogTemp, Display, TEXT("Starting DirectLink Simple Test..."));

    // 测试发送方
    UE_LOG(LogTemp, Display, TEXT("Setting up Sender..."));
    if (!UDirectLinkTestLibrary::SetupSender()) return false;
    if (!UDirectLinkTestLibrary::StartSender()) return false;
    
    UE_LOG(LogTemp, Display, TEXT("Sending scene: %s"), *TestScenePath);
    const bool bSendSuccess = UDirectLinkTestLibrary::SendScene(TestScenePath);
    UDirectLinkTestLibrary::StopSender();

    if (!bSendSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to send test scene."));
        return false;
    }

    // 测试接收方 (注意：实际应用中发送和接收通常是独立进程)
    UE_LOG(LogTemp, Display, TEXT("Setting up Receiver..."));
    if (!UDirectLinkTestLibrary::SetupReceiver()) return false;
    if (!UDirectLinkTestLibrary::StartReceiver()) return false;

    // 在真实场景中，此处应有延迟或等待外部数据发送的机制
    // 为演示目的，我们假设数据已准备好
    UE_LOG(LogTemp, Display, TEXT("Dumping received scene (if any)..."));
    UDirectLinkTestLibrary::DumpReceivedScene();
    
    UDirectLinkTestLibrary::StopReceiver();

    UE_LOG(LogTemp, Display, TEXT("DirectLink Simple Test Finished."));
    return true;
}
```

## 模块依赖

从 `DirectLinkTest.Build.cs` 的依赖关系分析，该模块是一个用于测试的运行时模块，其依赖相对集中。

| 模块 | 用途 |
|---|---|
| `DirectLink` | **核心依赖**。提供 DirectLink 通信的基础框架、端点管理、数据序列化等核心功能。 |
| `DatasmithCore` | 提供 Datasmith 场景数据模型（如 `FDatasmithScene`）的定义，用于构造和解析测试场景。 |
| `DatasmithRuntime` | 提供运行时加载和操作 Datasmith 场景数据的功能。 |
| `Json` | 可能用于配置或日志数据的序列化。 |

*注：为了使用此模块，你的 `Build.cs` 文件需要添加 `DirectLinkTest` 模块依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，将 double 常量截断为 float 时产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced new versions... | 废弃了旧的对象遍历函数，引入了新版本。属于引擎范围的API清理。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，确保正确使用预/后编辑更改包装。 |
| 2026-03-05 | `1adb9f68` | New material translator work: ... | 新的材质翻译器工作。 |

### 维护评价

- **年龄**：创建于2019年，已约7年。
- **更新频率**：近期的提交（2026年）均为**维护性、编译性或代码质量改进**（如修复警告、迁移API、代码清理），**没有新增功能或测试场景**。
- **维护状态**：属于**维护不活跃**。作为一个测试模块，在核心功能（DirectLink， Datasmith）稳定后，其代码基本处于“只修不改”的状态。
- **建议**：该模块适合作为**学习和调试 DirectLink 与 Datasmith 数据流**的参考工具，其函数调用方式清晰易懂。**不推荐将其直接用于生产环境**的自动化测试或核心逻辑中，因为它提供的测试节点过于基础，且缺乏完善的错误处理和状态管理。用于概念验证和初期调试非常合适。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/) （Datasmith 整体文档）
- 测试用例：该模块本身即为测试用例，其内部函数（如 `TestParameters`）和 `DirectLinkTestLibrary.h` 中的蓝图节点是主要的测试入口。引擎级别的 DirectLink 单元测试通常位于 `Engine/Tests/` 目录下。