# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制API |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl) | |

---

## 用途

Remote Control API 是一套完整的远程控制工具集，允许通过 HTTP 请求和 WebSocket 连接远程操控 Unreal Engine。它的核心解决的问题是：**让外部应用程序、Web 服务、虚拟制片设备能够实时读写引擎中的属性、调用函数、控制 Actor 状态**。

该插件在两个层面工作：

1. **运行时 Web 服务层**（WebRemoteControl 模块）：启动内嵌 HTTP/WebSocket 服务器，暴露 REST API 端点，供任何支持 HTTP 的客户端调用
2. **编辑器 UI 层**（RemoteControlUI 模块）：提供完整的编辑器面板，让用户在编辑器中将 Actor 属性、函数暴露为"远程可控制实体"，并配置控制器（Controller）、行为（Behaviour）、动作（Action）逻辑系统

与普通的 Blueprint RPC 不同，Remote Control 的特色在于：
- 无需编写代码即可通过 UI 暴露任意 UProperty 和 UFunction
- 支持多协议绑定（OSC、MIDI 等），通过 Protocol 模块扩展
- 提供分组、签名、多用户同步等高级功能
- 专为虚拟制片（Virtual Production）场景设计

## 使用场景

- 你在做虚拟制片 / LED Volume 拍摄，需要用 TouchOSC / Companion 等设备远程调节灯光参数 → 用 Remote Control 暴露灯光属性，通过 OSC/HTTP 控制
- 你需要构建一个 Web 控制面板，让导演在 iPad 上实时调整场景 → 用 Remote Control API 的 HTTP 端点
- 你需要在编辑器中创建复杂的"当控制器值变化时自动执行动作"的逻辑 → 用 Logic 系统（Controller → Behaviour → Action）
- 你需要让 Unreal 与媒体服务器（如 Disguise、Pixotope）双向通信 → 用 Remote Control Protocol 模块

---

## 蓝图用法

Remote Control API 主要通过编辑器 UI 和 C++ API 操作，蓝图 API 相对有限。主要的蓝图可访问功能集中在 RemoteControlLogic 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 暴露/取消暴露属性 | 通过编辑器面板在 Details 视图中右键暴露属性 | `SRemoteControlPanel` |
| 暴露函数 | 暴露 Actor 或 Blueprint 函数供远程调用 | `SRemoteControlPanel` |
| 创建控制器 | 在 Logic 面板中创建各种类型的虚拟属性控制器 | `SRCControllerPanel` |
| 添加行为 | 为控制器添加行为（条件触发、范围映射等） | `SRCBehaviourPanel` |
| 添加动作 | 为行为添加要执行的属性设置或函数调用动作 | `SRCActionPanel` |

### 使用示例（编辑器操作流程）

**暴露一个属性并远程控制：**

1. 打开 Remote Control Preset 资产（Content Browser → 右键 → Remote Control Preset）
2. 在编辑器中选中目标 Actor，在 Details 面板中找到要暴露的属性
3. 点击属性旁的"眼睛"图标（Remote Control 行扩展按钮），将属性暴露到 RC 面板
4. 在 RC 面板的 Exposed Entities 列表中可以看到该属性
5. 切换到 Protocols 模式，配置 OSC/HTTP 绑定地址
6. 从外部应用通过 HTTP `PUT /remote/preset/{presetId}/entity/{entityId}` 修改属性值

**配置 Logic 系统（控制器-行为-动作）：**

1. 在 RC 面板中切换到 Controller 标签
2. 点击"+"创建一个 Controller（如 Float 类型）
3. 切换到 Behaviour 标签，选择 Controller，添加 Behaviour（如 Conditional）
4. 切换到 Action 标签，添加 Action 绑定到已暴露的属性
5. 当 Controller 值变化时，Behaviour 会根据条件触发 Action 改变目标属性

---

## C++ 用法

### 头文件引入

```cpp
#include "IRemoteControlUIModule.h"
#include "RemoteControlPreset.h"
#include "RemoteControlEntity.h"
#include "RemoteControlField.h"
```

### 基本用法：获取模块并创建面板

```cpp
// 来源: Source/RemoteControlUI/Private/RemoteControlUIModule.h

// 获取 Remote Control UI 模块单例
IRemoteControlUIModule& RCModule = IRemoteControlUIModule::Get();

// 获取当前正在编辑的 Remote Control Preset
URemoteControlPreset* ActivePreset = RCModule.GetActivePreset();
```

### 进阶用法：注册自定义属性过滤器

```cpp
// 来源: Source/RemoteControlUI/Public/IRemoteControlUIModule.h

// 注册一个自定义属性过滤器，决定哪些属性可以在 Details 面板中暴露
IRemoteControlUIModule& RCModule = IRemoteControlUIModule::Get();

FDelegateHandle FilterHandle = RCModule.AddPropertyFilter(
    FOnDisplayExposeIcon::CreateLambda([](const FRCExposesPropertyArgs& InArgs) -> bool
    {
        // 返回 true 表示该属性可以暴露，false 表示隐藏暴露图标
        FProperty* Property = InArgs.GetProperty();
        if (Property && Property->HasMetaData(TEXT("NoRemoteControl")))
        {
            return false;
        }
        return true;
    })
);

// 移除过滤器
RCModule.RemovePropertyFilter(FilterHandle);
```

### 进阶用法：注册自定义元数据显示

```cpp
// 来源: Source/RemoteControlUI/Public/IRemoteControlUIModule.h

// 注册元数据自定义，定制实体详情面板中特定元数据项的显示方式
IRemoteControlUIModule& RCModule = IRemoteControlUIModule::Get();

RCModule.RegisterMetadataCustomization(
    FName("MyCustomMetadata"),
    FOnCustomizeMetadataEntry::CreateLambda([](
        URemoteControlPreset* Preset,
        const FGuid& DisplayedEntityId,
        IDetailLayoutBuilder& LayoutBuilder,
        IDetailCategoryBuilder& CategoryBuilder)
    {
        // 自定义元数据条目在详情面板中的显示
    })
);
```

### 进阶用法：注册自定义 Widget 工厂

```cpp
// 来源: Source/RemoteControlUI/Public/IRemoteControlUIModule.h

// 为特定类型的 Remote Control Entity 注册自定义 Widget 工厂
IRemoteControlUIModule& RCModule = IRemoteControlUIModule::Get();

RCModule.RegisterWidgetFactoryForType(
    FRemoteControlProperty::StaticStruct(),
    FOnGenerateRCWidget::CreateLambda([](const FGenerateWidgetArgs& Args) -> TSharedPtr<SRCPanelTreeNode>
    {
        // 返回自定义的面板节点 Widget
        return nullptr;
    })
);
```

### 进阶用法：注册属性解析器

```cpp
// 来源: Source/RemoteControlUI/Public/IRemoteControlUIModule.h

// 注册自定义属性源解析器，用于特殊类型的属性绑定
IRemoteControlUIModule& RCModule = IRemoteControlUIModule::Get();

RCModule.RegisterPropertyResolver(
    FName("DisplayClusterResolver"),
    FRCPropertyResolver::CreateStatic(&FRemoteControlUIModule::ResolveDisplayClusterConfigurationDataProperty)
);
```

---

## Demo 示例

以下示例展示如何在编辑器插件中扩展 Remote Control 面板的功能：

```cpp
// MyRCExtension.h
#pragma once

#include "CoreMinimal.h"
#include "IRemoteControlUIModule.h"

class FMyRCExtension
{
public:
    void Register()
    {
        IRemoteControlUIModule& RCModule = IRemoteControlUIModule::Get();

        // 注册暴露图标过滤器
        PropertyFilterHandle = RCModule.AddPropertyFilter(
            FOnDisplayExposeIcon::CreateRaw(this, &FMyRCExtension::ShouldDisplayExposeIcon)
        );

        // 注册暴露实体面板扩展
        RCModule.RegisterExposedEntitiesPanelExtender(
            MakeShared<FMyPanelExtender>()
        );
    }

    void Unregister()
    {
        IRemoteControlUIModule& RCModule = IRemoteControlUIModule::Get();
        RCModule.RemovePropertyFilter(PropertyFilterHandle);
        // RCModule.UnregisterExposedEntitiesPanelExtender(...);
    }

private:
    bool ShouldDisplayExposeIcon(const FRCExposesPropertyArgs& InArgs) const
    {
        // 允许所有属性暴露
        return true;
    }

    FDelegateHandle PropertyFilterHandle;
};
```

```cpp
// MyRCExtension.cpp
#include "MyRCExtension.h"

// 注册/反注册通常在编辑器模块的 StartupModule/ShutdownModule 中调用
// FMyRCExtension Extension;
// Extension.Register();
```

---

## 模块依赖

从各模块的 Build.cs 分析，以下为该插件独特的依赖关系：

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 核心运行时模块，Remote Control Preset 资产和实体管理 |
| `RemoteControlCommon` | 共享类型定义和协议通用接口 |
| `RemoteControlLogic` | 逻辑系统：Controller/Behaviour/Action 数据模型 |
| `RemoteControlProtocol` | 协议抽象层，支持 OSC、MIDI 等外部协议绑定 |
| `WebRemoteControl` | 内嵌 HTTP/WebSocket 服务器，提供 REST API |
| `RemoteControlMultiUser` | 多用户编辑支持，同步 Remote Control 状态 |
| `RemoteControlUI` | 编辑器 UI 面板，暴露属性的编辑器集成 |
| `StructUtils` | Property Bag 支持，用于虚拟属性控制器 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1716f2e0` | Remote Control: added missing ApplyColorWheelDelta and ApplyColorGradingWheelDelta to the built-in a | 补充了内置 Action 缺失的色轮相关操作函数 |
| 2026-05-20 | `d724bb52` | Remote Control: fixed uninitialized ObjectClass in FRCRemoteFunctionCallParams, sometimes causing a | 修复远程函数调用参数中 ObjectClass 未初始化导致的崩溃 |
| 2026-05-20 | `12d5ae7f` | Remote Control: added allow list for remote function calls, and specifying built-in functions to all | 新增远程函数调用白名单机制，指定内置函数允许被远程调用 |
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | Motion Design 相关调整，间接影响 RC 面板布局 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 到 float 截断警告 |

### 维护评价

- **创建时间**：2019 年 6 月，已有约 7 年历史
- **更新频率**：非常活跃，2026 年 5 月有多次功能性更新和 Bug 修复
- **维护状态**：**活跃维护中** — 作为 Virtual Production 工作流的核心组件，Epic 持续投入开发
- **代码规模**：465 个源文件，8 个模块，属于大型插件
- **已知限制**：UI 模块（RemoteControlUI）虽然标记为 Runtime 类型，但其大量依赖编辑器 API（Slate、Details View、PropertyRowGenerator 等），实际只能在编辑器中使用
- **推荐程度**：✅ **强烈推荐** — 如果你需要虚拟制片远程控制能力，这是官方标准方案，文档完善且持续更新

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/RemoteControl/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl/Tests)