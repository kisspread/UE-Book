# Remote Control Actor Modifier Bridge

> Interface between the Remote Control, Actor Modifier and Property Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制Actor修改器桥 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlActorModifierBridge` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlActorModifierBridge) | |

## 用途

该插件作为 **RemoteControl**、**ActorModifierCore**（Actor 修改器）和 **PropertyAnimatorCore**（属性动画器）三者之间的桥梁。  
它在启动时自动注册一个属性解析器，当通过 RemoteControl 系统操作某个 Remote Control 属性时，解析器会检查该属性是否绑定到某个 Actor Modifier 的对象路径或属性路径，并将解析出的对象与属性路径返回给动画系统，从而允许：

- 在 Remote Control 面板中直接控制 Actor Modifier 的暴露属性；
- 使用 Property Animator 为 Actor Modifier 的属性制作动画；
- 将 Actor Modifier 中编辑的修改器效果通过 Remote Control 暴露给外部（如 Web 应用、蓝图、信使）。

由于该插件**仅作为桥梁**，用户无需手动调用其 API，它会在编辑器启动时自动生效，将三个子系统无缝连接。

## 使用场景

- 你正在使用 **Actor Modifier Core**（`ActorModifierCore`）为场景中的 Actor 添加动态修改器（如位置、缩放、材质参数等），并希望通过 Remote Control 面板来实时调整这些修改器的参数值。
- 你计划使用 **Property Animator Core**（`PropertyAnimatorCore`）为某个 Actor Modifier 的属性创建关键帧动画，但动画系统默认无法识别 Actor Modifier 中的属性；此桥接插件使得动画系统能正确解析并驱动这些属性。
- 你希望将 Actor Modifier 的修改器参数暴露给外部遥控应用（如手机平板上的 Remote Control App），而无需手动编写数据传输逻辑。

## 蓝图用法

该插件没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性，因为它完全在编辑器层面自动工作。  
但是，通过它你可以直接使用其他插件的现有节点来操作 Actor Modifier 的属性：

- **Remote Control Preset**：创建 Remote Control Preset，将 Actor Modifier 中的属性添加到 Preset 中（支持`Set Remote Control Property`蓝图节点）。
- **Property Animator**：在动画轨道中直接选取 Actor Modifier 的属性作为动画目标。

具体方法：

1. 确保已启用 `RemoteControl`, `ActorModifierCore`, `PropertyAnimatorCore`, `OperatorStack` 及本插件。
2. 在场景中创建一个带有 ACtor Modifier 组件的 Actor（例如使用 `ActorModifierCore` 提供的 `ActorModifierBase` 子类）。
3. 打开 **Remote Control Preset** 编辑器，选择该 Actor 的修改器组件，并将其可暴露属性添加到 Preset。
4. 在蓝图或动画蓝图中，使用 Remote Control 的 `Set Remote Control Property` 节点控制该属性。

## C++ 用法

该插件不提供公开的 C++ 函数或类供用户直接调用。其核心是一个私有模块类 `FRemoteControlActorModifierBridgeModule`，在 `StartupModule` 中注册一个属性解析回调。

### 头文件引入

```cpp
// 你不需要直接包含本插件的任何头文件，它会在编辑器启动时自动完成桥接。
```

### 基本用法

本插件自动工作，无需用户代码介入。以下是一个如何在 C++ 中通过 RemoteControl 操作 Actor Modifier 的示例（假设你已经创建了 Remote Control Preset）：

```cpp
// 使用 RemoteControl 系统设置 Actor Modifier 属性
#include "IRemoteControlModule.h"
#include "ActorModifierCore/ActorModifierBase.h" // 取决于你使用的修改器类

void SetActorModifierProperty(UObject* InWorldContext, const FString& InPresetName, const FString& InPropertyPath, float InNewValue)
{
    if (IRemoteControlModule* RCModule = FModuleManager::LoadModulePtr<IRemoteControlModule>("RemoteControl"))
    {
        // 从 Preset 获取对应的 FRCObjectReference
        TSharedPtr<FRemoteControlProperty> RCProp = RCModule->ResolvePresetProperty(InPresetName, InPropertyPath);
        if (RCProp.IsValid())
        {
            // 桥接插件已确保 Actor Modifier 的属性路径能被正确解析
            // 直接设置值
            RCModule->SetObjectProperties(RCProp->GetBoundObjects()[0], RCProp->GetPropertyPath(), InNewValue);
        }
    }
}
```

### 进阶用法

（无进一步进阶用法，桥接插件仅处理属性路径解析。）

## Demo 示例

提供一个最小的编辑器模块演示，展示如何启用插件并验证桥接生效。  
假设你要创建一个编辑器工具，列表显示当前场景中所有能被桥接的 Actor Modifier 属性。

```cpp
// MyActorModifierBridgeDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMyActorModifierBridgeDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnPostEngineInit();
    void LogBridgeInfo();
};
```

```cpp
// MyActorModifierBridgeDemo.cpp
#include "MyActorModifierBridgeDemo.h"
#include "IRemoteControlModule.h"
#include "ActorModifierCore/Public/ActorModifierCoreSubsystem.h"
#include "PropertyAnimatorCore/Public/PropertyAnimatorCoreSubsystem.h"

IMPLEMENT_MODULE(FMyActorModifierBridgeDemoModule, MyActorModifierBridgeDemo);

void FMyActorModifierBridgeDemoModule::StartupModule()
{
    // 在引擎初始化完成后检查插件是否生效
    if (!IsRunningCommandlet())
    {
        FCoreDelegates::OnPostEngineInit.AddRaw(this, &FMyActorModifierBridgeDemoModule::OnPostEngineInit);
    }
}

void FMyActorModifierBridgeDemoModule::ShutdownModule()
{
    FCoreDelegates::OnPostEngineInit.RemoveAll(this);
}

void FMyActorModifierBridgeDemoModule::OnPostEngineInit()
{
    LogBridgeInfo();
}

void FMyActorModifierBridgeDemoModule::LogBridgeInfo()
{
    IRemoteControlModule* RCModule = FModuleManager::GetModulePtr<IRemoteControlModule>("RemoteControl");
    if (RCModule)
    {
        // 桥接插件注册了一个属性解析器，这里可以遍历 Preset 检查
        UE_LOG(LogTemp, Log, TEXT("RemoteControl Module loaded. Bridge plugin auto-resolves ActorModifier properties."));
    }
}
```

## 模块依赖

使用本插件时，你的模块的 `Build.cs` 需要添加以下依赖（非标准、本插件特有的依赖）：

| 模块 | 用途 |
|---|---|
| `ActorModifierCore` | 提供 Actor Modifier 组件与核心系统 |
| `OperatorStack` | 操作堆栈，用于撤销/重做等编辑器功能 |
| `RemoteControl` | 远程控制预设与属性解析系统 |
| `PropertyAnimatorCore` | 属性动画系统，用于驱动 Actor Modifier 属性 |

**备注**：以上均为必需依赖，但通常它们也会被你的项目直接或间接引用。如果项目未启用这些插件，本插件将无法工作。

## 维护状态

### 近期更新

| 日期 | Hash | Commit |
|---|---|---|
| 2025-07-28 | `558e1e82` | Remote Control / Actor Modifier / Property Animator: Bridge plugin |

### 维护评价

- **创建时间**：2025-07-28（距今约 3 个月）
- **更新频率**：仅有初始提交，无后续更新
- **活跃度**：未观察到活跃维护，但作为一个初版桥梁插件，可能后续会随相关系统更新而更新
- **已知问题**：实验性阶段，可能存在未发现的兼容性或性能问题
- **推荐使用**：如果你是这三个插件的重度用户，并且需要它们之间互通，可以试用。建议在非生产环境中先行验证。

**警告**：距离上次更新已超过 1 个月，但考虑到插件全新发布，尚不能断定已停止维护。使用时请关注引擎后续版本中该插件的变更。

## 相关链接

- [源码 (Plugin Root)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlActorModifierBridge)
- [官方文档](https://docs.unrealengine.com/) – 目前无单独文档页，请参考 RemoteControl、ActorModifierCore、PropertyAnimatorCore 的独立文档。
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlActorModifierBridge) – 此插件未提供单独的测试目录，相关测试可能位于各依赖插件的测试集中。