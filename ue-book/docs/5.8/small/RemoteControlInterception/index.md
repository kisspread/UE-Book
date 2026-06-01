# Remote Control Interception API

> Plugin that allows to intercept Remote Control commands（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制拦截接口 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlInterception` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlInterception) | |

## 用途

这个插件的核心目的是为 Unreal Engine 的 Remote Control 系统提供一个**可扩展的拦截框架**。它本身不包含任何具体的拦截或处理逻辑，而是定义了一组抽象接口和数据结构。

其存在意义在于**解耦**：允许其他模块（如自定义的远程控制应用、安全审计工具、网络同步逻辑）在不直接依赖 `RemoteControl` 核心模块的前提下，注册并实现自己的拦截器（Interceptor）或处理器（Processor）。当 Remote Control 系统接收到一个外部命令（如修改属性、调用函数）时，可以通过这些接口将命令元数据分发给已注册的拦截器，从而实现命令的验证、修改、日志记录或完全重定向。

简单来说，它为 Remote Control 命令的“中间件”处理提供了一个标准化的插槽。

## 使用场景

- **虚拟制片（Virtual Production）**：在现场拍摄时，通过自定义的 iPad 应用控制场景灯光，但希望在实际执行前，通过一个自定义的拦截器验证灯光参数的范围或记录操作日志。
- **安全与访问控制**：实现自定义的远程控制权限系统。在属性被修改或函数被调用前，检查当前连接的客户端是否有权限执行该操作。
- **操作日志与审计**：记录所有通过 Remote Control 系统进行的远程操作，用于后期复盘或问题排查。
- **协议转换与参数修改**：拦截传入的命令，并根据自定义逻辑动态修改其参数值，然后再传递给引擎执行。

## 蓝图用法

该插件是一个纯 C++ 接口定义库，没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性给蓝图系统。其设计目标是供 C++ 模块使用。

## C++ 用法

该插件的核心是两个模板接口类和一组元数据结构。使用时，你需要创建一个类来实现 `IRemoteControlInterceptionFeatureInterceptor` 或 `IRemoteControlInterceptionFeatureProcessor` 接口，并将其作为模块特性（Modular Feature）注册。

### 头文件引入

```cpp
#include "IRemoteControlInterceptionFeature.h"
```

### 基本用法

最简单的用法是实现一个拦截器，在属性设置前记录日志。

（来源：基于 `IRemoteControlInterceptionFeature.h` 和 `IRemoteControlInterceptionCommands.h` 的接口定义）

```cpp
// MyInterceptor.h
#pragma once

#include "IRemoteControlInterceptionFeature.h"

class FMyInterceptor : public IRemoteControlInterceptionFeatureInterceptor
{
public:
    FMyInterceptor();
    virtual ~FMyInterceptor();

    // IRemoteControlInterceptionCommands<ERCIResponse> 接口实现
    virtual ERCIResponse SetObjectProperties(FRCIPropertiesMetadata& InObjectProperties) override;
    virtual ERCIResponse ResetObjectProperties(FRCIObjectMetadata& InObject) override;
    virtual ERCIResponse InvokeCall(FRCIFunctionMetadata& InFunction) override;
    virtual ERCIResponse SetPresetController(FRCIControllerMetadata& InController) override;
};

// MyInterceptor.cpp
#include "MyInterceptor.h"
#include "Modules/ModuleManager.h"

FMyInterceptor::FMyInterceptor()
{
    // 在构造时，将自己注册为模块特性
    IModularFeatures::Get().RegisterModularFeature(GetName(), this);
}

FMyInterceptor::~FMyInterceptor()
{
    // 在析构时，从模块特性中注销
    IModularFeatures::Get().UnregisterModularFeature(GetName(), this);
}

ERCIResponse FMyInterceptor::SetObjectProperties(FRCIPropertiesMetadata& InObjectProperties)
{
    // 这里可以添加自定义逻辑，例如验证、日志记录
    UE_LOG(LogTemp, Warning, TEXT("拦截到属性设置: 对象 %s, 属性 %s"),
        *InObjectProperties.ObjectPath,
        *InObjectProperties.PropertyPath);

    // 返回 Apply 表示让 Remote Control 系统继续执行该命令
    // 返回 Intercept 表示命令被拦截，Remote Control 不会执行它
    return ERCIResponse::Apply;
}

ERCIResponse FMyInterceptor::ResetObjectProperties(FRCIObjectMetadata& InObject)
{
    UE_LOG(LogTemp, Warning, TEXT("拦截到属性重置: 对象 %s"), *InObject.ObjectPath);
    return ERCIResponse::Apply;
}

ERCIResponse FMyInterceptor::InvokeCall(FRCIFunctionMetadata& InFunction)
{
    UE_LOG(LogTemp, Warning, TEXT("拦截到函数调用: %s"), *InFunction.FunctionPath);
    return ERCIResponse::Apply;
}

ERCIResponse FMyInterceptor::SetPresetController(FRCIControllerMetadata& InController)
{
    UE_LOG(LogTemp, Warning, TEXT("拦截到预设控制器设置: %s - %s"),
        *InController.Preset.ToString(),
        *InController.Controller.ToString());
    return ERCIResponse::Apply;
}
```

### 进阶用法

可以实现一个处理器（Processor），它不拦截命令（不阻止执行），而是纯粹地“处理”或“转发”它们，例如将命令通过网络发送给另一个监控进程。

（来源：结合 `IRemoteControlInterceptionFeatureProcessor` 和 `FRCIObjectMetadata` 的使用）

```cpp
// MyProcessor.h
#pragma once

#include "IRemoteControlInterceptionFeature.h"

class FMyProcessor : public IRemoteControlInterceptionFeatureProcessor
{
public:
    FMyProcessor();
    virtual ~FMyProcessor();

    // 处理器接口，返回类型为 void
    virtual void SetObjectProperties(FRCIPropertiesMetadata& InObjectProperties) override;
    // ... 其他接口类似
};

// MyProcessor.cpp
#include "MyProcessor.h"

FMyProcessor::FMyProcessor()
{
    IModularFeatures::Get().RegisterModularFeature(GetName(), this);
}

FMyProcessor::~FMyProcessor()
{
    IModularFeatures::Get().UnregisterModularFeature(GetName(), this);
}

void FMyProcessor::SetObjectProperties(FRCIPropertiesMetadata& InObjectProperties)
{
    if (InObjectProperties.IsValid())
    {
        // 假设我们有一个网络发送函数
        // SendOverNetwork(InObjectProperties.PayloadType, InObjectProperties.Payload);
        UE_LOG(LogTemp, Log, TEXT("处理器正在处理属性设置，准备转发数据包 (长度: %d)"),
            InObjectProperties.Payload.Num());
    }
}
```

## Demo 示例

以下是一个完整的、可编译的最小拦截器示例。它实现了 `IRemoteControlInterceptionFeatureInterceptor`，在属性被修改时打印一条警告日志，并选择不拦截该命令（返回 `Apply`）。

**MyRCInterceptorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyRCInterceptorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FMyInterceptor> InterceptorInstance;
};
```

**MyRCInterceptorModule.cpp**
```cpp
#include "MyRCInterceptorModule.h"
#include "IRemoteControlInterceptionFeature.h"

// 定义拦截器类
class FMyInterceptor : public IRemoteControlInterceptionFeatureInterceptor
{
public:
    FMyInterceptor() = default;
    virtual ~FMyInterceptor() = default;

    // 实现接口：在属性设置时，打印日志并允许执行
    virtual ERCIResponse SetObjectProperties(FRCIPropertiesMetadata& InObjectProperties) override
    {
        UE_LOG(LogTemp, Warning, TEXT("[RC拦截器] 拦截到属性设置请求: %s.%s"),
            *InObjectProperties.ObjectPath, *InObjectProperties.PropertyPath);
        // 允许 Remote Control 系统继续执行此命令
        return ERCIResponse::Apply;
    }

    // 为了演示，其他接口简化处理，全部放行
    virtual ERCIResponse ResetObjectProperties(FRCIObjectMetadata& InObject) override { return ERCIResponse::Apply; }
    virtual ERCIResponse InvokeCall(FRCIFunctionMetadata& InFunction) override { return ERCIResponse::Apply; }
    virtual ERCIResponse SetPresetController(FRCIControllerMetadata& InController) override { return ERCIResponse::Apply; }
};

// 模块实现
void FMyRCInterceptorModule::StartupModule()
{
    // 创建拦截器实例
    InterceptorInstance = MakeShareable(new FMyInterceptor());
    // 注册为模块特性，这样 Remote Control 系统就能发现它
    IModularFeatures::Get().RegisterModularFeature(
        IRemoteControlInterceptionFeatureInterceptor::GetName(),
        InterceptorInstance.Get());
}

void FMyRCInterceptorModule::ShutdownModule()
{
    // 注销模块特性
    if (InterceptorInstance.IsValid())
    {
        IModularFeatures::Get().UnregisterModularFeature(
            IRemoteControlInterceptionFeatureInterceptor::GetName(),
            InterceptorInstance.Get());
        InterceptorInstance.Reset();
    }
}

// 模块注册宏
IMPLEMENT_MODULE(FMyRCInterceptorModule, MyRCInterceptor)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的模块 (`RemoteControlInterception`) 主要定义了接口和数据结构，对其他模块的直接链接依赖非常少，其核心价值在于被其他需要拦截功能的模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除了 Motion Design 插件的 beta 标记，未直接涉及此插件。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新了内置插件的供应商链接，使用安全协议。 |
| 2022-08-26 | `c6e87912` | [EpicStageApp] Fix stage app failing to control nDisplay nodes when connected directly | 修复了 EpicStageApp 直连时无法控制 nDisplay 节点的问题。 |

### 维护评价

该插件**维护不活跃**。
- 它创建于 2021 年 4 月，是 Unreal Engine 5 早期的一部分。
- 核心接口和结构体在创建后基本没有功能性更新。
- 近期的提交（如 2025 年的 `77ee7eae`）多是仓库级的维护或与其他 Virtual Production 插件打包的改动，而非针对此插件本身的增强或修复。
- 最后一次与插件功能直接相关的实质性改动记录是 2022 年 5 月 (`39825987`) 的 Web Remote Control 事务控制。
- **建议**：该插件提供的是稳定的底层接口。如果你的项目依赖于自定义 Remote Control 拦截功能，并且当前接口满足需求，可以安全使用。但不要期待近期会有新功能或活跃的维护。如果遇到问题，可能需要自行排查或寻找替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlInterception)
- 官方文档：无
- 测试用例：未发现位于此插件目录内的专用测试文件。