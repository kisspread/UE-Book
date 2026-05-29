# Live Link Master Lockit

> Live Link support for the Ambient MasterLockit metadata server

| 属性 | 值 |
|---|---|
| 中文名 | 主锁元服务器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（类型未知，插件标记为可包含内容） |
| 模块 | `LiveLinkMasterLockit` (Runtime), `LiveLinkMasterLockitEditor` (Runtime) |
| 实验性 | ⚚ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit) | |

## 用途

该插件为 Unreal Engine 的 Live Link 框架提供了对 **Ambient MasterLockit** 设备的数据源支持。Ambient MasterLockit 是影视制作中常用的设备，用于时间码同步和元数据管理（如场景、镜头、卷号等）。通过此插件，虚幻引擎可以实时接收来自 MasterLockit 设备的元数据，并将其同步到场景中的 Actor 或通过 Live Link 系统广播，从而实现虚拟制片流程中的设备状态同步与记录。

**核心解决的问题**：在虚拟制片（Virtual Production）或影视后期制作中，需要将来自现场同步设备（如 Ambient 的 Lockit 系列）的元数据（时间码、场景编号等）与虚幻引擎内的场景数据自动关联。此插件充当了连接器，使得这些外部设备数据能被引擎的 Live Link 系统识别和使用。

## 使用场景

- 你在使用 **Ambient MasterLockit** 或兼容设备进行多机位拍摄时间码同步。
- 你需要将现场设备的 **场景（Scene）、镜头（Shot）、卷（Take）** 等元数据实时输入到虚幻编辑器或运行时，用于驱动字幕、UI 显示或自动记录。
- 你在进行 **虚拟制片（Virtual Production）**，需要确保引擎中的镜头状态与现场拍摄设备保持同步。

## 蓝图用法

根据提供的头文件分析，该插件的编辑器模块主要提供了一个用于创建和配置源的 Slate 面板（`SLiveLinkMasterLockitSourcePanel`），其核心功能通过该面板暴露。直接的 `BlueprintCallable` 函数可能较少，主要功能通过 Live Link 的通用节点进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateNewSource` | 根据配置创建一个新的 MasterLockit 数据源连接。此方法在源面板 UI 中使用。 | `SLiveLinkMasterLockitSourcePanel` |

### 使用示例（蓝图描述）

在蓝图中使用时，你通常不会直接调用此插件的特定节点。而是：
1. 通过 **Live Link** 面板，点击 “+” 按钮添加源。
2. 在源类型列表中选择 “Ambient MasterLockit”。
3. 此时会弹出一个由 `SLiveLinkMasterLockitSourcePanel` 构建的配置面板，输入目标设备的 IP 地址等连接信息。
4. 源创建成功后，即可在 Live Link Subject 列表中看到对应的 MasterLockit 数据流（包含时间码、场景等），然后像使用其他 Live Link 数据一样在蓝图中使用 `Get Live Link Data` 等节点。

## C++ 用法

插件提供了一个运行时模块和一个编辑器模块。编辑器模块主要负责用户界面和源工厂注册。

### 头文件引入

```cpp
// 编辑器模块（用于源工厂或UI扩展）
#include "LiveLinkMasterLockitEditorModule.h"
```

### 基本用法

该插件的主要 C++ 交互点是编辑器模块的启动与关闭，以及源面板的创建。以下基于 `LiveLinkMasterLockitEditorModule.h` 展示模块结构：

```cpp
// 引自: Source/LiveLinkMasterLockitEditor/Private/LiveLinkMasterLockitEditorModule.h

// 模块类的标准接口实现，通常在插件加载/卸载时自动调用，无需手动操作
class FLiveLinkMasterLockitEditorModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### 进阶用法

更深入的用法涉及自定义或扩展源面板。`SLiveLinkMasterLockitSourcePanel` 负责收集连接设置并触发源创建：

```cpp
// 引自: Source/LiveLinkMasterLockitEditor/Private/LiveLinkMasterLockitSourcePanel.h

// 自定义 Slate 面板，用于显示 MasterLockit 连接设置
class SLiveLinkMasterLockitSourcePanel : public SCompoundWidget
{
    // ... (Slate 参数定义)

public:
    void Construct(const FArguments& Args);

    // 由UI按钮调用，验证并创建源
    FReply CreateNewSource(bool bShouldCreateSource);

private:
    // 存储用户输入的连接设置（如IP地址）
    FLiveLinkMasterLockitConnectionSettings ConnectionSettings;

    // 对创建该面板的源工厂的弱引用
    TWeakObjectPtr<const ULiveLinkMasterLockitSourceFactory> SourceFactory;

    // 源创建完成后的回调委托
    ULiveLinkSourceFactory::FOnLiveLinkSourceCreated OnSourceCreated;
};
```

**注意**：由于此插件为 `Installed: false`（默认未安装）且为 `IsBetaVersion: true`，其完整的 C++ API（特别是运行时模块中用于处理接收到的元数据的类）可能未在提供的头文件片段中完全展示。实际使用中，你更可能通过 Live Link 的通用接口来订阅和消费此源产生的 Subject 数据。

## Demo 示例

由于插件主要是提供数据源接入，其核心逻辑在于建立连接而非暴露大量客户端 API。以下是一个概念性示例，展示如何在代码中触发与 `SLiveLinkMasterLockitSourcePanel` 类似的源创建过程（实际中通常通过编辑器 UI 操作）：

**DemoLiveLinkMasterLockit.h**
```cpp
#pragma once

#include "CoreMinimal.h"

// 一个简单的演示类，模拟通过代码启动 MasterLockit 连接的过程
class FDemoLiveLinkMasterLockit
{
public:
    // 尝试使用给定的设置创建 MasterLockit Live Link 源
    // 注意：此函数主要演示流程，实际参数和依赖需要根据插件内部类调整
    static bool TryCreateMasterLockitSource(const FString& InTargetIpAddress);
};
```

**DemoLiveLinkMasterLockit.cpp**
```cpp
#include "DemoLiveLinkMasterLockit.h"
#include "ILiveLinkClient.h"
#include "LiveLinkMasterLockitSourceFactory.h" // 假设的源工厂头文件

bool FDemoLiveLinkMasterLockit::TryCreateMasterLockitSource(const FString& InTargetIpAddress)
{
    // 1. 获取 Live Link 客户端接口
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (!ModularFeatures.IsModularFeatureAvailable(ILiveLinkClient::ModularFeatureName))
    {
        UE_LOG(LogTemp, Error, TEXT("LiveLinkClient interface not available."));
        return false;
    }
    ILiveLinkClient* LiveLinkClient = &ModularFeatures.GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);

    // 2. 查找 MasterLockit 的源工厂
    ULiveLinkMasterLockitSourceFactory* Factory = FindObject<ULiveLinkMasterLockitSourceFactory>(GetTransientPackage(), TEXT("MasterLockitFactory"));
    if (!Factory)
    {
        // 在实际应用中，工厂对象可能需要通过特定方式获取或实例化
        UE_LOG(LogTemp, Warning, TEXT("MasterLockit source factory not found. Typically this is done via the UI."));
        return false;
    }

    // 3. 准备创建参数（这里需要填充 FLiveLinkMasterLockitConnectionSettings）
    // 注意：以下为示意，具体参数结构请参考插件源码
    FLiveLinkMasterLockitConnectionSettings Settings;
    Settings.TargetIpAddress = InTargetIpAddress;
    // ... 设置其他参数

    // 4. 创建源（此过程内部会建立网络连接）
    TSharedPtr<ILiveLinkSource> NewSource = Factory->CreateSource(Settings);
    if (NewSource.IsValid())
    {
        LiveLinkClient->AddSource(NewSource);
        UE_LOG(LogTemp, Log, TEXT("Successfully added MasterLockit source for IP: %s"), *InTargetIpAddress);
        return true;
    }

    UE_LOG(LogTemp, Error, TEXT("Failed to create MasterLockit source."));
    return false;
}
```

## 模块依赖

根据插件的功能和常见模式，其 `Build.cs` 文件很可能依赖以下模块。由于未提供实际 `Build.cs`，以下是基于功能的合理推断：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架接口，是此插件的基础 |
| `Json` | 用于解析来自 MasterLockit 设备的 JSON 格式元数据 |
| `Networking` 或 `Sockets` | 用于实现与 MasterLockit 设备的 UDP/TCP 通信 |
| `LiveLinkInterface` | Live Link 源和主题的接口定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量被截断为 float 的编译警告。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString 两种字符串类型。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为 UE_LOGF 格式。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复，以节省内存。 |
| 2024-10-29 | `4fb04fde` | Add support for creating json objects from utf8 strings, and utf8 strings from json objects | 新增从 UTF-8 字符串创建 JSON 对象以及从 JSON 对象生成 UTF-8 字符串的支持。 |

### 维护评价

**综合评价：维护不活跃，不推荐用于关键新项目。**

- **创建时间与年龄**：插件创建于 2021 年 3 月，至今约 4 年。
- **更新频率与内容**：最近 5 次更新（截止 2026 年 5 月）均为**底层重构和代码维护**（如修复警告、内存优化、日志迁移），**没有任何功能性增强或新特性的记录**。最后一次有意义的日期停在 2024 年 10 月。
- **维护状态**：虽然近期（2026 年）仍有编译和底层库的适配性提交，但这表明它仍在引擎的“大扫除”中被照顾到，**并非由其功能驱动的活跃开发**。核心功能在创建后似乎已进入维护期。
- **已知限制**：插件标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，说明它仍处于实验阶段，未被认为达到生产就绪状态。
- **推荐度**：如果你的项目**强烈依赖 Ambient MasterLockit 设备**且找不到替代方案，可以谨慎使用。但对于新的虚拟制片项目，建议优先评估 Epic 官方更活跃支持的 Live Link 源或第三方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit)
- 官方文档
- 测试用例