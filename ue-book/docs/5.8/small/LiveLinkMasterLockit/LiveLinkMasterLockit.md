# LiveLinkMasterLockit

> Live Link support for the Ambient MasterLockit metadata server

| 属性 | 值 |
|---|---|
| 中文名 | 主锁同步源 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，材质模板） |
| 模块 | `LiveLinkMasterLockit` (Runtime), `LiveLinkMasterLockitEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit) | |

## 用途

该插件是 **Live Link** 的一个数据源，用于与 **Ambient MasterLockit** 设备进行通信。MasterLockit 是一个用于多机位拍摄现场的时间码同步和元数据服务器。此插件的主要功能是通过网络（TCP/IP）连接到 MasterLockit 服务器，实时接收并解析从该服务器发送的 **镜头元数据包**，特别是针对 **蔡司（Zeiss）** 镜头的数据（如焦距、焦点距离、光圈等）。

它解决的问题是：在虚拟制片（Virtual Production）流程中，需要将物理摄影机镜头的实时参数（对焦、变焦、光圈等）同步到 Unreal Engine 内的虚拟摄像机或 CG 元素上，确保画面参数匹配。该插件为此提供了一个标准化的接口，将 MasterLockit 设备的数据转换为 Live Link 可消费的源。

## 使用场景

- 你在使用多台摄影机进行 **虚拟制片**，并且现场部署了 Ambient MasterLockit 系统来同步时间码和管理镜头元数据。
- 你需要将现场摄影机的 **真实镜头参数**（如蔡司 CP.3 镜头的焦点、光圈、焦距）实时传输到 UE 中，用于驱动虚拟镜头的景深、视角或进行数据记录。
- 你希望利用 Live Link 框架，统一管理和路由来自不同设备（包括镜头元数据）的数据流。

## 蓝图用法

该插件主要作为 Live Link 源工厂，在编辑器中通过 Live Link 面板进行配置和创建，**不直接提供可供蓝图调用的函数**。其核心交互是配置性的。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 插件通过 `ULiveLinkMasterLockitSourceFactory` 在 Live Link 面板中提供创建界面 | `ULiveLinkMasterLockitSourceFactory` |

### 使用示例（蓝图描述）

1.  在编辑器中，打开 **Live Link** 窗口（通常位于“窗口”->“虚拟制片”->“Live Link”）。
2.  点击 **源** 下拉菜单，选择 **MasterLockit**。
3.  在弹出的连接面板中，输入 MasterLockit 服务器的 **IP 地址**（例如 `192.168.1.100`）。
4.  设置一个用于在 Live Link 中标识此源的 **主题名称**（例如 `DirectorCam`）。
5.  点击创建。连接成功后，Live Link 面板中将出现一个新的源，并可能创建一个对应的主题，其中包含从该设备接收到的镜头数据。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkMasterLockitConnectionSettings.h"
#include "LiveLinkMasterLockitFactory.h"
```

### 基本用法

以下代码演示如何通过 C++ 创建一个 MasterLockit Live Link 源（通常用于自定义工具或自动化流程）。

```cpp
// 来源：自定义工具逻辑，基于源码 API
#include "LiveLinkMasterLockitConnectionSettings.h"
#include "LiveLinkMasterLockitFactory.h"

void CreateMasterLockitSource()
{
    // 1. 配置连接参数
    FLiveLinkMasterLockitConnectionSettings Settings;
    Settings.IPAddress = TEXT("192.168.1.100"); // MasterLockit 服务器 IP
    Settings.SubjectName = FName(TEXT("MainCamera")); // 在 Live Link 中的名称

    // 2. 生成连接字符串 (内部方法，通常由工厂使用)
    FString ConnectionString = ULiveLinkMasterLockitSourceFactory::CreateConnectionString(Settings);

    // 3. 使用工厂创建源
    ULiveLinkMasterLockitSourceFactory* Factory = NewObject<ULiveLinkMasterLockitSourceFactory>();
    TSharedPtr<ILiveLinkSource> NewSource = Factory->CreateSource(ConnectionString);

    // 源创建后会尝试自动连接。
    // 更常见的方式是在编辑器 Live Link 面板中操作，C++ 创建用于高级场景。
}
```

### 进阶用法

该插件的功能主要通过其内部的 `FMasterLockitMessageThread` 和 `FLiveLinkMasterLockitSource` 类实现。对于开发者而言，扩展点通常在于：
-   **自定义设置类**：`ULiveLinkMasterLockitSourceSettings` 可被子类化以存储额外的配置数据。
-   **数据处理**：通过实现 `FLiveLinkMasterLockitSource` 中的 `OnFrameDataReady_AnyThread` 回调（在私有模块中），可以干预原始 `FLensPacket` 数据的解析过程，但此接口未在公共头文件中暴露，属于插件内部逻辑。

## Demo 示例

一个最小化的 C++ 示例，展示如何创建源对象。**注意**：直接通过 C++ 创建 Live Link 源并不常见，更推荐通过编辑器 UI 操作。

```cpp
// MyLiveLinkTool.h
#pragma once

#include "CoreMinimal.h"

class FMyLiveLinkTool
{
public:
    static void SpawnMasterLockitSource(const FString& InIP, const FName& InSubjectName);
};
```

```cpp
// MyLiveLinkTool.cpp
#include "MyLiveLinkTool.h"
#include "LiveLinkMasterLockitConnectionSettings.h"
#include "LiveLinkMasterLockitFactory.h"

void FMyLiveLinkTool::SpawnMasterLockitSource(const FString& InIP, const FName& InSubjectName)
{
    // 准备连接设置
    FLiveLinkMasterLockitConnectionSettings Settings;
    Settings.IPAddress = InIP;
    Settings.SubjectName = InSubjectName;

    // 通过工厂创建源
    ULiveLinkMasterLockitSourceFactory* Factory = NewObject<ULiveLinkMasterLockitSourceFactory>();
    TSharedPtr<ILiveLinkSource> Source = Factory->CreateSource(ULiveLinkMasterLockitSourceFactory::CreateConnectionString(Settings));

    if (Source.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created MasterLockit Live Link source for %s"), *InIP);
    }
}
```

## 模块依赖

从源码头文件的引用推断，使用此插件或其衍生模块需要以下依赖：

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 核心接口，提供 `ILiveLinkSource`, `ILiveLinkClient` 等 |
| `LiveLink` | Live Link 运行时实现和管理 |
| `SlateCore`, `Slate` | 用于创建源工厂中的创建面板UI (`SWidget`) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 的编译器警告。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString（底层JSON库改动）。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF（日志系统宏更新）。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存（底层JSON库优化）。 |
| 2024-10-29 | `4fb04fde` | Add support for creating json objects from utf8 strings, and utf8 strings from json objects | 为 FJsonObject 添加从 UTF-8 字符串创建和导出的支持（底层JSON库功能）。 |

### 维护评价

该插件自 2021 年创建以来，**长期处于实验性（Beta）状态**，且默认未启用。最近的几次提交均为针对底层引擎模块（如 FJsonObject）的全局性编译修复和重构，**并非针对该插件本身的功能性更新或 Bug 修复**。最后一次对插件功能有影响的实质性更新可能发生在很久之前。

**综合评价**：这是一个 **维护不活跃** 的实验性插件。它作为一个特定硬件（Ambient MasterLockit）的接口，功能相对稳定，但也意味着它依赖于外部硬件 API，且未被 Epic 作为核心功能持续投入开发。对于生产环境，需要自行验证其与当前 UE 版本和目标硬件固件的兼容性。仅推荐有明确 MasterLockit 设备集成需求的团队使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit)
- 官方文档（无）
- [Live Link 通用文档](https://docs.unrealengine.com/5.8/en-US/live-link-in-unreal-engine/)