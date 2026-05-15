# USDPregen

> Library to assist with pre-generating USD-based content.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 预生成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `UsdPregenCore` (Editor), `USDPregenHttpWorker` (Runtime), `USDPregenInterchange` (Runtime), `USDPregenInterchangeEditor` (Runtime), `USDPregenPy` (Runtime), `USDPregenUObjectStorage` (Runtime), `USDPregenWrapper` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen) | |

## 用途

USDPregen 是一个用于在 Unreal Engine 中批量预生成基于 USD（Universal Scene Description）资源的基础设施插件。它解决了以下核心问题：

- **远程资源获取**：通过 HTTP Worker 模块从远程服务器拉取 USD 资源
- **资产路径管理**：支持用户可配置的模板字符串，使用占位符动态确定生成资产的路径
- **资产格式转换**：通过 Interchange 模块将 USD 资产转换为 UE 原生格式
- **Python 脚本集成**：允许使用 Python 脚本自动化预生成工作流
- **存储管理**：提供 UObject 存储后端，用于持久化预生成结果

该插件的核心价值在于将 USD 资产的预处理流水线化，特别适合需要批量导入大量 USD 资产（如影视、建筑可视化项目）的场景。所有模块默认以 Runtime 类型加载，确保可在编辑器和运行时环境下工作。

## 使用场景

- 你需要从远程服务器批量拉取 USD 模型并转换为 UE 资产 → 用 USDPregen 的 HTTP Worker + Interchange 管线
- 你需要自定义资产输出路径规则（如按日期、项目、类型组织）→ 用模板字符串占位符系统
- 你需要使用 Python 脚本自动化 USD 资产的预生成流程 → 用 USDPregenPy 模块
- 你在做影视级别的资产流水线，需要处理大量 USD 场景描述文件 → 用整个 USDPregen 插件

## 蓝图用法

> ⚠️ 当前 USDPregenPy 模块头文件中未暴露 `BlueprintCallable` 函数。蓝图 API 可能存在于其他子模块（如 USDPregenWrapper、USDPregenCore）中。以下信息基于当前可见接口推断。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 暂无公开蓝图节点 | USDPregenPy 模块主要通过 Python 脚本接口工作，而非蓝图 | — |

> **提示**：该插件的主要用户交互方式为 Python 脚本调用，而非蓝图可视化编程。请参阅 [Python 用法](#python-用法) 章节。

## C++ 用法

### 头文件引入

```cpp
#include "USDPregenPyModule.h"
```

### 基本用法

USDPregenPy 是一个模块接口，主要负责在引擎启动时注册 Python 绑定。开发者通常不需要直接实例化该模块类，而是通过模块加载系统自动管理：

```cpp
#include "Modules/ModuleManager.h"

// 获取 USDPregenPy 模块实例（通常由引擎自动加载）
FUSDPregenPyModule& PregenPyModule = FModuleManager::GetModuleChecked<FUSDPregenPyModule>("USDPregenPy");
```

### 进阶用法

USDPregenPy 模块依赖 Python3，它为 USDPregen 的核心功能暴露 Python 绑定。典型的使用模式是通过 Python 脚本调用 USDPregen 的预生成管线：

```cpp
// 通过其他子模块的 C++ API 进行预生成
// USDPregenPy 模块本身主要在 StartupModule() 中注册 Python 可调用函数
// 实际的预生成逻辑分布在 UsdPregenCore、USDPregenHttpWorker 等模块中
```

## Demo 示例

### USDPregenPyModule.h

```cpp
// 自定义 USDPregen Py 模块扩展示例
#pragma once

#include "Modules/ModuleInterface.h"

class FMyPregenPyExtension : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### USDPregenPyModule.cpp

```cpp
#include "USDPregenPyModule.h"
#include "Modules/ModuleManager.h"

void FUSDPregenPyModule::StartupModule()
{
    // 模块启动时注册 Python 绑定
    // USDPregenPy 依赖 Python3 模块
    // 在此处初始化 USD 预生成相关的 Python 可调用函数
}

void FUSDPregenPyModule::ShutdownModule()
{
    // 清理 Python 绑定和模块资源
}

IMPLEMENT_MODULE(FUSDPregenPyModule, USDPregenPy)
```

## 模块依赖

从 Build.cs 分析，USDPregenPy 模块具有以下依赖：

| 模块 | 用途 |
|---|---|
| `Python3` | Python 解释器集成，用于注册 Python 调用绑定 |
| `USDPregenCore` (插件内) | 预生成核心逻辑 |
| `USDPregenWrapper` (插件内) | USD 封装层 |

> **注意**：由于 USDPregenPy 是 USDPregen 插件的一部分，使用时通常需要同时启用整个 USDPregen 插件及其依赖模块。

## 维护状态

### 近期更新

- `9e86e007` 2026-05-14 — [USD] UsdPregen: Fixes regression introduced by recent clean up, where an item can get incorrectly p — *修复了最近清理工作中引入的回归问题，某项条目可能被错误处理*
- `ddc18470` 2026-05-14 — [USD] UsdPregen: On definition conflicts during registry population, return the existing definition — *在注册表填充期间遇到定义冲突时，返回已有定义而非报错*
- `60206a86` 2026-05-14 — USD Pregen: Batch renaming for consistency. Also changes the default storage plugin in UE to the UOb — *批量重命名以保持一致性，默认存储插件更改为 UObject 存储*
- `bad2257d` 2026-05-14 — USD Pregen: User-configurable template string with placeholders for deterimining asset path; — *新增用户可配置的模板字符串，使用占位符确定资产路径*
- `9f286b30` 2026-05-14 — USD Pregen: Fix _VT and _NonVT textures not being saved from worker imports. — *修复 Worker 导入时 _VT 和 _NonVT 纹理未被保存的问题*

### 维护评价

**⚠️ 实验性新插件**

- **创建时间**：2026-05-14，极新的插件
- **最后更新**：2026-05-14（同日多次提交，活跃开发中）
- **版本状态**：`IsBetaVersion=true`，`IsExperimentalVersion=true`，`EnabledByDefault=false`
- **开发阶段**：处于早期积极开发阶段，同日提交中既有新功能（模板字符串）也有回归修复
- **API 稳定性**：接口可能随时变更，不建议在生产环境使用
- **推荐程度**：仅建议用于实验性项目或内部工具开发，等待 API 稳定后再考虑生产使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen)
- [源码 - USDPregenPy 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen/Source/USDPregenPy)
- 官方文档（暂无）
- 测试用例（暂未发现）