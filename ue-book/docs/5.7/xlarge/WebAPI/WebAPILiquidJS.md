# WebAPI

> Automated generation of web based APIs

| 属性 | 值 |
|---|---|
| 中文名 | LiquidJS 代码生成器 |
| 分类 | Web |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码生成模板、Node.js 后端脚本） |
| 模块 | `WebAPI` (Runtime), `WebAPIBlueprintGraph` (Runtime), `WebAPIEditor` (Runtime), `WebAPILiquidJS` (Runtime), `WebAPIOpenAPI` (Runtime), `PLUGIN_NAMEGenerated` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI) | |

---

## 用途

WebAPI 插件是一套用于**自动生成 Web 风格 API 代码**的工具集。它支持从 OpenAPI 规范（Swagger）自动生成 C++ 或蓝图函数库，帮助开发者快速搭建基于 REST 或 WebSocket 的服务端/客户端代码。

`WebAPILiquidJS` 模块是 WebAPI 的可选代码生成后端，使用 [LiquidJS](https://liquidjs.com/) 模板引擎（JavaScript 实现）驱动代码生成。它需要启动一个外部 Node.js 进程，监听指定端口，接收代码生成请求并返回结果。相比默认的代码生成器，LiquidJS 模块提供了更灵活的模板自定义能力，适合需要对生成代码样式进行深度定制的团队。

---

## 使用场景

- **需要自定义代码生成模板**：如果你对 WebAPI 默认的 C++ 代码风格不满意，或者需要生成特定格式的蓝图节点，可以使用 LiquidJS 模板。
- **已有 LiquidJS 模板资源**：团队积累了 LiquidJS 模板库，可以无缝接入。
- **希望集成外部渲染服务**：例如使用 Kubernetes 部署模板渲染服务。

---

## 蓝图用法

本模块暴露的蓝图节点较少，核心功能通过 C++ 配置和自动化流程控制。主要设置通过项目设置即可完成。

### 设置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get WebAPI LiquidJS Settings` | 获取 LiquidJS 模块的开发者设置对象（在项目设置中配置端口、自动启动等） | `UWebAPILiquidJSSettings` （蓝图中可直接通过 `GetClassDefaults` 或 `GetDefaultObject` 获取，无独立蓝图节点） |

> 注意：`UWebAPILiquidJSSettings` 并非 `BlueprintCallable`，但在编辑器设置面板中可直接配置端口、服务地址等信息。

---

## C++ 用法

### 头文件引入

```cpp
#include "WebAPILiquidJS/Public/IWebAPILiquidJSModule.h"
#include "WebAPILiquidJS/Public/WebAPILiquidJSSettings.h"
```

### 基本用法

1. **获取模块实例并手动启动/关闭 Web App**

```cpp
// 获取 LiquidJS 模块
if (IWebAPILiquidJSModuleInterface* LiquidJSModule = FModuleManager::GetModulePtr<IWebAPILiquidJSModuleInterface>("WebAPILiquidJS"))
{
    // 手动启动外部 Node.js 进程（通常由模块自动启动，此函数用于重试或手动管理）
    LiquidJSModule->TryStartWebApp();
}
```

2. **访问设置并修改端口**

```cpp
const UWebAPILiquidJSSettings* Settings = UWebAPILiquidJSSettings::Get();
UE_LOG(LogTemp, Log, TEXT("LiquidJS Port: %u"), Settings->Port);

// 创建设置有 GetDefault<UWebAPILiquidJSSettings>() 等，修改需在 Config/DefaultEngine.ini 中
// 或使用 UDeveloperSettings 的 SaveConfig
```

3. **使用代码生成器生成文件**

```cpp
// 获取 LiquidJS 代码生成器实例
UWebAPILiquidJSCodeGenerator* Generator = NewObject<UWebAPILiquidJSCodeGenerator>();
TWeakObjectPtr<UWebAPIDefinition> Definition = ...; // 从 WebAPI 编辑器获取定义
TSharedPtr<FWebAPICodeGenFile> File = MakeShared<FWebAPICodeGenFile>();
// 填充 File 内容...

// 异步生成
Generator->GenerateFile(Definition, File).Then([](EWebAPIGenerationResult Result)
{
    // 处理生成结果
});
```

### 进阶用法

**主动控制外部进程状态**

`FWebAPILiquidJSProcess` 提供了低层级 API 来启动/关闭 Node.js 进程，通常不需要直接使用，但可用于自定义生命周期管理：

```cpp
// 获取进程对象（在模块内部调用）
// 实际上进程对象是模块私有的，可通过接口函数间接控制
```

---

## Demo 示例

本示例展示如何通过 C++ 设置 LiquidJS 作为代码生成器，并手动触发一次生成。

### DemoCodeGen.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "WebAPIDefinition.h"
#include "WebAPILiquidJSCodeGenerator.h"

class FDemoCodeGen
{
public:
    static void RunLiquidJSGeneration()
    {
        // 1. 确保 LiquidJS 模块已加载
        FModuleManager::Get().LoadModuleChecked("WebAPILiquidJS");

        // 2. 获取一个测试定义（真实场景从编辑器数据获取）
        UWebAPIDefinition* Definition = NewObject<UWebAPIDefinition>();
        // 填充 Definition 的 Schema（略）

        // 3. 创建 LiquidJS 生成器
        UWebAPILiquidJSCodeGenerator* Generator = NewObject<UWebAPILiquidJSCodeGenerator>();

        // 4. 创建要生成的文件描述
        TSharedPtr<FWebAPICodeGenFile> File = MakeShared<FWebAPICodeGenFile>();
        File->Name = TEXT("MyGeneratedClass");
        File->Namespace = TEXT("MyAPI");
        // 根据实际需要填充更多字段...

        // 5. 异步生成
        TFuture<EWebAPIGenerationResult> Future = Generator->GenerateFile(Definition, File);
        Future.Then([](EWebAPIGenerationResult Result)
        {
            UE_LOG(LogTemp, Log, TEXT("LiquidJS generation completed with result: %d"), static_cast<int32>(Result));
        });
    }
};
```

### DemoCodeGen.cpp

```cpp
#include "DemoCodeGen.h"

// 在游戏启动或某个时机调用
// FDemoCodeGen::RunLiquidJSGeneration();
```

---

## 模块依赖

**注意**：`WebAPILiquidJS` 依赖于外部 Node.js 环境（运行时），需要用户自行安装 Node.js（≥16.0.0）。首次启动时会自动编译 `WebAPI/WebAPILiquidJS/Source/WebApp` 下的脚本。

| 模块 | 用途 |
|---|---|
| `WebAPI` | 核心 API 定义和代码生成框架 |
| `WebAPIEditor` （仅开发时?） | 编辑器工具，提供 UI 来管理和触发生成 |
| `Projects` | 插件路径查找 |
| `DeveloperSettings` | 设置界面支持 |
| `Sockets` / `Networking` | 内部通信使用（HTTP/WebSocket 服务） |
| `Json` / `JsonUtilities` | JSON 解析和序列化 |

（非标准依赖均已列出）

---

## 维护状态

### 近期更新

| 日期 | 提交 | 说明 |
|---|---|---|
| 2025-07-31 | `399ed9f8` | 修复 Windows/Mac 平台进程创建句柄传递 |
| 2025-06-11 | `afdf8d75` | 替换 FORCEINLINE 为 inline (Online 模块相关，非本模块直接修改) |
| 2024-11-22 | `36771d79` | 修正同时标记 Experimental 和 Beta 的插件描述文件 |
| 2024-11-20 | `e2fe1c9e` | 修复 MustImplement 元数据更名为 ObjectMustImplement |
| 2024-11-15 | `a2c3875d` | 初始提交（WebAPI 插件包含 LiquidJS 模块） |

### 维护评价

- **创建时间**：~2024年11月15日，至今不足1年。
- **更新频率**：最近一次实质性更新在 2025-07-31（修复进程创建），之前有几次编译警告修复和元数据调整，无重大功能更新。
- **活跃度**：维护不活跃，但作为实验性插件，未出现长期停滞。
- **已知限制**：
  - 需要外部 Node.js 环境，增加部署复杂度。
  - 模板文件路径硬编码在插件内部，自定义模板需要修改源码。
  - 文档较少，仅从源码可获取 API。
- **推荐使用**：不建议用于生产环境，适合探索自动代码生成或需要高度定制模板的团队。

---

## 相关链接

- [源码（5.7分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Web/WebAPI/Tests)（可能为空）
- [LiquidJS 官方网站](https://liquidjs.com/)