# GPU Reshape Plugin

> GPU Reshape editor integration

| 属性 | 值 |
|---|---|
| 中文名 | GPU 重整形工具 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GPUReshape` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2025-05-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GPUReshape) | |

## 用途

GPUReshape 是 Epic 提供的开发者工具插件，用于集成 GPU Reshape 应用程序到 Unreal Editor 中。GPU Reshape 是一个 GPU 调试/分析工具（类似 PIX 或 RenderDoc），本插件负责：

1. **环境引导（Bootstrapping）**：自动查找并安装 GPU Reshape 的 Loader（注入器），将分析工具挂载到当前编辑器进程中
2. **应用启动管理**：通过编辑器按钮或控制台命令一键打开 GPU Reshape 应用程序，并自动附加当前工作区
3. **进程生命周期管理**：管理外部 GPU Reshape 应用的进程句柄，提供初始化状态查询

本质上，它是一个"胶水"插件，让你在编辑器内直接启动和连接 GPU Reshape 工具，无需手动配置注入环境。

## 使用场景

- 你需要对项目的 GPU 渲染进行性能分析或调试 → 使用 GPU Reshape 插件快速连接 GPU Reshape 应用
- 你在开发渲染功能时需要检查 GPU 端的实际执行情况 → 点击编辑器工具栏按钮即可启动并自动附加
- 你需要在调试会话中保持应用连接状态 → 插件管理进程生命周期，避免手动重复配置

## 蓝图用法

本插件不暴露任何 `BlueprintCallable` 函数。它是一个纯开发者工具插件，所有交互通过编辑器 UI（工具栏按钮）和控制台命令完成。

### 控制台命令

| 命令 | 说明 |
|---|---|
| `OpenApp`（推测） | 通过 `FAutoConsoleCommand` 注册的控制台命令，打开 GPU Reshape 应用程序 |

## C++ 用法

本插件是开发者工具，没有面向其他模块的公共 API。以下为模块内部的关键接口供参考：

### 核心类

```cpp
// Source/GPUReshape/Private/GPUReshapeModule.h
class FGPUReshapeModule : public IModuleInterface
```

| 方法 | 说明 |
|---|---|
| `OpenOrSwitchToApp()` | 打开 GPU Reshape 应用，如果已打开则切换过去 |
| `SwitchToApp()` | 切换到已打开的 GPU Reshape 应用窗口 |
| `IsInitialized()` | 查询 Loader 是否已成功安装和初始化 |
| `GetAppGetProcessID()` | 获取 GPU Reshape 应用的进程 ID |

## Demo 示例

本插件不提供面向开发者的扩展 API，无需 Demo。使用方式为：

1. 确保 GPU Reshape 插件已启用（默认已启用）
2. 在编辑器中找到工具栏上的 GPU Reshape 按钮（类似 PIX/RenderDoc 风格）
3. 点击按钮，插件会自动查找 Loader、安装注入、启动 GPU Reshape 应用并附加工作区

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-03-09 | `5d05ec9a` | GPU Reshape [addressing feedback], automatically set symbol and source paths | 根据反馈改进，自动设置符号和源码路径 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前查找替换错误后的重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退 CL51314860 的改动 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 迁移 OnPostEngineInit 委托 API 以修复注册缺失问题 |

### 维护评价

- **创建时间**：2025 年 5 月，是一个非常新的插件
- **活跃度**：维护活跃，最近一次更新在 2026 年 4 月，持续有功能改进和 bug 修复
- **稳定性**：2026 年 2 月有一次回退和重做，表明当时 API 在调整中；之后趋于稳定
- **平台限制**：仅支持 Win64，不支持 Server 目标（作为 GPU 工具这是合理的）
- **推荐度**：✅ 推荐使用。这是一个活跃维护的官方开发者工具，适合需要 GPU 性能分析的开发工作流

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/GPUReshape)