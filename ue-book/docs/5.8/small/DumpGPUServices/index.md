# Dump GPU Services

> Implements automatic upload services for the DumpGPU command.

| 属性 | 值 |
|---|---|
| 中文名 | GPU 转储上传服务 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DumpGPUServices` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DumpGPUServices) | |

## 用途

该插件为引擎的 `DumpGPU` 调试命令提供自动上传服务。`DumpGPU` 是一个用于捕获 GPU 渲染状态（如 Render Graph、资源、Pass 信息等）的诊断工具，而本插件为这些捕获的数据提供上传至远程服务器的能力，方便团队协作分析渲染问题。

插件不包含任何游戏内容，仅作为渲染调试基础设施的一部分存在。目标排除列表明确禁止在 **Server** 目标和 **Shipping** 配置中加载，表明这是一个纯粹的开发调试工具。

## 使用场景

- 你在调试复杂的渲染问题（如 Pass 排序错误、资源泄漏），需要将 `DumpGPU` 捕获的数据上传至共享服务器供团队分析
- 你在进行渲染功能的 Code Review，需要远程分享 GPU 状态快照
- 你需要在多台设备间同步 GPU 转储数据进行对比分析

## 蓝图用法

该插件不暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有功能通过引擎控制台命令 `DumpGPU` 触发，上传服务在后台自动运行。

## C++ 用法

### 头文件引入

```cpp
#include "IDumpGPUServices.h"
```

### 基本用法

该插件仅提供模块接口，用于检查模块是否可用。实际的 `DumpGPU` 和上传功能通过引擎控制台命令调用，无需直接 C++ 集成。

```cpp
// 检查 DumpGPUServices 模块是否已加载
if (IDumpGPUServices::IsAvailable())
{
    IDumpGPUServices& DumpGPUServices = IDumpGPUServices::Get();
    // 模块已就绪，DumpGPU -upload 命令可正常使用
}
```

来源：`Source/DumpGPUServices/Public/IDumpGPUServices.h`

### 控制台命令用法

该插件的功能通过控制台命令触发，无需编写 C++ 代码：

```
// 执行 GPU 转储并自动上传
DumpGPU -upload
```

## Demo 示例

```cpp
// MyDebugHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyDebugHelper
{
public:
    static void CaptureAndUploadGPUState()
    {
        // 通过控制台命令触发 DumpGPU 并上传
        if (GEngine)
        {
            GEngine->Exec(nullptr, TEXT("DumpGPU -upload"));
        }
    }
};
```

```cpp
// MyDebugHelper.cpp
#include "MyDebugHelper.h"
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新 API |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理 5.2 版本废弃的头文件包含宏 |
| 2024-01-19 | `f0294685` | Fixed up a lot of bool-taking container resize functions to take EAllowShrinking instead. | 适配容器 resize API 签名变更 |
| 2023-02-21 | `8676f608` | Moving DumpGPU to Public so that DumpGPUServices can access it correctly. | 将 DumpGPU 符号移至 Public 以修复访问权限 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件批量更新 |

### 维护评价

该插件创建于 2022 年 3 月，代码量极小（4 个文件），功能边界清晰。近年来的提交均为引擎级 API 适配和编译修复，无功能性更新。插件仍标记为 **实验性**（`IsExperimentalVersion=true`），且未见稳定性提升计划。

作为 `DumpGPU` 命令的上传后端，其存在依赖于引擎渲染调试系统的整体架构。当前状态属于**维护型**——不会主动发展，但会随引擎 API 变更被动更新。

**推荐使用**：如果你的团队需要共享 GPU 转储数据，该插件默认启用，无需额外配置。但需注意其**实验性**标记，不建议在生产环境的最终构建中依赖它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/DumpGPUServices)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)（无专属测试，DumpGPU 功能测试位于引擎测试目录）