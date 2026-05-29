# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI资产） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件提供了一套完整的实时面部/身体动画数据流传输方案。它解决了从外部面部捕捉设备（如 iPhone 上的 Live Link Face 应用）将动画数据实时传输到 UE5 中 MetaHuman 角色的核心需求。

插件包含三个层次的 Live Link 源：
1. **LiveLinkFaceSource**：连接远程 Live Link Face 应用，通过网络接收面部捕捉数据
2. **MetaHumanLiveLinkSource**：MetaHuman 专用的 Live Link 源，处理 MetaHuman 特有的动画数据格式
3. **MetaHumanLocalLiveLinkSource**：本地 Live Link 源，用于本地处理或测试场景

配套的编辑器模块提供了设备发现、连接配置面板等 UI 工具，简化了连接流程。

## 使用场景

- 你在使用 iPhone + Live Link Face 应用进行面部动捕 → 用 LiveLinkFaceSource 自动发现并连接设备
- 你需要将实时面部动画应用到 MetaHuman 角色 → 用 MetaHumanLiveLinkSource 作为 Live Link 数据源
- 你需要在编辑器中配置并管理多个 Live Link 面部追踪连接 → 用编辑器模块提供的详情面板定制
- 你在进行虚拟直播或实时预览 → 通过本插件将面部捕捉数据实时映射到 MetaHuman

## 蓝图用法

本插件主要面向编辑器工作流，核心功能通过 Live Link 框架和编辑器面板暴露。直接的蓝图节点较少，但可通过 Live Link 面板进行可视化配置。

### 核心节点

本插件的功能主要通过编辑器面板暴露，而非直接蓝图节点。核心交互通过以下方式：

| 功能 | 说明 | 所在模块 |
|---|---|---|
| 设备发现面板 | 自动扫描局域网内 Live Link Face 设备 | `LiveLinkFaceSourceEditor` |
| 连接配置 | 手动输入 IP 地址和端口连接设备 | `LiveLinkFaceSourceEditor` |
| Live Link 源注册 | 在 Live Link 面板中选择 MetaHuman 源 | `MetaHumanLiveLinkSource` |

### 使用示例（编辑器面板操作）

1. 打开 **Window → Live Link** 面板
2. 在 Source 下拉菜单中选择 **Live Link Face** 源
3. 插件会自动扫描局域网内可用的 Live Link Face 设备
4. 在发现面板中双击目标设备即可连接
5. 或手动输入 IP 地址和端口号进行连接
6. 配置 Subject Name 以标识数据源
7. 在 MetaHuman 角色的动画蓝图中引用该 Live Link 主题

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkFaceDiscovery.h"
#include "LiveLinkFaceSourceSettings.h"
```

### 基本用法 — 创建设备发现实例

从 `FLiveLinkFaceSourceCustomization` 中提取的用法，用于扫描局域网内的 Live Link Face 设备：

```cpp
// 来源: Source/LiveLinkFaceSourceEditor/Private/LiveLinkFaceSourceCustomization.h

#include "LiveLinkFaceDiscovery.h"

// 创建设备发现实例
TSharedRef<FLiveLinkFaceDiscovery> Discovery = MakeShared<FLiveLinkFaceDiscovery>();

// 获取发现的服务器列表
TArray<TSharedPtr<FLiveLinkFaceDiscovery::FServer>> Servers;
// Discovery 会自动扫描局域网，结果通过回调返回
```

### 进阶用法 — 自定义详情面板

从 `FLiveLinkFaceSourceCustomization` 提取，展示如何为 Live Link Face 源创建自定义编辑器面板：

```cpp
// 来源: Source/LiveLinkFaceSourceEditor/Private/LiveLinkFaceSourceCustomization.h

#include "IDetailCustomization.h"
#include "LiveLinkFaceDiscovery.h"
#include "SLiveLinkFaceDiscoveryPanel.h"

class FMyLiveLinkCustomization : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance()
    {
        return MakeShareable(new FMyLiveLinkCustomization());
    }

    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override
    {
        // 自定义详情面板布局
        // 添加地址输入框、端口输入框、Subject Name 输入框
        // 嵌入设备发现面板
    }

private:
    TSharedRef<FLiveLinkFaceDiscovery> LiveLinkFaceDiscovery;
    TArray<TSharedPtr<FLiveLinkFaceDiscovery::FServer>> ListServers;
};
```

## Demo 示例

以下展示如何在编辑器模块中注册自定义的 Live Link 面板：

```cpp
// MyLiveLinkModule.h
#pragma once

#include "Modules/ModuleManager.h"
#include "LiveLinkFaceDiscovery.h"

class FMyLiveLinkModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    TArray<FName> ClassesToUnregisterOnShutdown;
};

// MyLiveLinkModule.cpp
#include "MyLiveLinkModule.h"

void FMyLiveLinkModule::StartupModule()
{
    // 在引擎初始化后注册自定义面板
    FCoreDelegates::OnPostEngineInit.AddRaw(this, &FMyLiveLinkModule::PostEngineInit);
}

void FMyLiveLinkModule::ShutdownModule()
{
    // 清理注册的类
    for (const FName& ClassName : ClassesToUnregisterOnShutdown)
    {
        // Unregister customization classes
    }
}

void FMyLiveLinkModule::PostEngineInit()
{
    // 此时安全地注册面板定制
}

IMPLEMENT_MODULE(FMyLiveLinkModule, MyLiveLink)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 框架核心，提供数据传输通道 |
| `LiveLinkInterface` | Live Link 接口定义 |
| `MediaUtils` | 媒体工具（用于视频流处理） |
| `Media` | 媒体框架基础 |
| `EditorWidgets` | 编辑器 UI 控件（MetaHumanLocalLiveLinkSource 使用） |
| `PropertyEditor` | 属性面板定制（MetaHumanLocalLiveLinkSource 使用） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 暴露身体检测阈值参数 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 面部动画序列导出适配组合求解 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的警告 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | Apple 平台改用 AvfMedia 处理文件媒体源 |
| 2026-05-12 | `fa06fada` | New ADA model | 更新 ADA 模型 |

### 维护评价

- **状态**：🟢 活跃维护中
- **创建时间**：2025年2月，约1年历史，属于较新的插件
- **更新频率**：最近一周内有多次提交，更新非常频繁
- **更新内容**：涵盖功能增强（身体检测阈值、ADA 模型）、平台适配（Apple 媒体源）、编译修复等多个方面
- **建议**：作为 MetaHuman 工具链的核心组件，该插件受到 Epic 团队的持续关注和维护，推荐在 MetaHuman 实时动画工作流中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman/)（MetaHuman 整体文档）