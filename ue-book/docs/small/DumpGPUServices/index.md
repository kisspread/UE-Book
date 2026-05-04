# Dump GPU Services

> Implements automatic upload services for the DumpGPU command.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | DumpGPUServices (Runtime) |
| 创建时间 | 2022-03-24 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/DumpGPUServices) | |

## 用途

DumpGPUServices 是 UE5 `DumpGPU` 命令的配套上传服务插件。`DumpGPU` 功能（位于 RenderCore 模块）可以将 GPU 渲染管线的中间状态 dump 到本地磁盘，用于离线调试和分析渲染问题。DumpGPUServices 的作用是：**在 dump 完成后，自动将文件通过 HTTP 上传到远程服务器**，方便团队共享分析结果。

具体来说，这个插件做了三件事：

1. **读取配置** — 从 `Engine.ini` 的 `[Rendering.DumpGPUServices]` 段读取 `UploadURLPattern` 配置项
2. **创建 HTTP 上传 Provider** — 实现 `IDumpGPUUploadServiceProvider` 接口，注册到全局的 `GProvider` 指针
3. **执行上传** — 当 `DumpGPU` 命令完成后，自动递归遍历 dump 目录中的所有文件，通过 HTTP PUT 请求逐个上传，并支持可选的压缩传输

插件在编辑器环境下还会显示上传进度通知，上传完成后自动在浏览器中打开 dump 结果页面。

## 使用场景

- 你在团队中做 GPU 调试，需要把 `DumpGPU` 的结果自动推送到团队的分析服务器
- 你希望 dump 完成后自动清理本地文件（上传成功后会自动删除 dump 目录）
- 你需要在编辑器中看到上传进度，而不是手动上传文件

## 蓝图用法

此插件没有暴露任何蓝图接口。它是一个纯 Runtime 服务模块，通过全局 Provider 模式与 `DumpGPU` 系统集成。

## C++ 用法

### 头文件引入

```cpp
#include "IDumpGPUServices.h"
#include "DumpGPU.h"  // 来自 RenderCore 模块
```

### 基本用法

此插件的核心功能是作为 `DumpGPU` 的后端上传服务，**不需要手动调用**。只需正确配置，`DumpGPU` 命令执行完毕后会自动触发上传。

插件通过检查 `IDumpGPUUploadServiceProvider::GProvider` 全局指针来判断是否有可用的上传服务：

```cpp
// 来自 RenderCore/Public/DumpGPU.h
// 任何上传 Provider 都需要实现此接口
class IDumpGPUUploadServiceProvider
{
public:
    virtual void UploadDump(const FDumpParameters& Parameters) = 0;
    static IDumpGPUUploadServiceProvider* GProvider;  // 全局单例
};
```

DumpGPUServices 插件在 `StartupModule()` 中读取配置并注册自己的 Provider：

```cpp
// 来自 Source/DumpGPUServices/Private/DumpGPUServices.cpp
void FDumpGPUServices::StartupModule()
{
    // 如果已经有其他 Provider 注册，跳过
    if (IDumpGPUUploadServiceProvider::GProvider)
        return;

    FString UploadURLPattern;
    GConfig->GetString(TEXT("Rendering.DumpGPUServices"), TEXT("UploadURLPattern"), 
                       UploadURLPattern, GEngineIni);

    // 如果项目没有配置，尝试使用引擎默认值（NotForLicensees 配置）
    if (UploadURLPattern.IsEmpty())
    {
        UploadURLPattern = TEXT(DUMPGPU_SERVICES_DEFAULT_URL_PATTERN);
    }

    // 当前只支持 http:// 协议
    if (UploadURLPattern.StartsWith(TEXT("http://")))
    {
        UploadProvider = CreateHTTPUploadProvider(UploadURLPattern);
    }

    if (UploadProvider)
    {
        IDumpGPUUploadServiceProvider::GProvider = UploadProvider;
    }
}
```

### 配置方式

在 `Engine.ini`（或项目的 `DefaultEngine.ini`）中添加：

```ini
[Rendering.DumpGPUServices]
UploadURLPattern=http://your-dump-server:8080/dumps/[Project]/[Platform]/[DumpTime]-[DumpType]
```

URL 中支持以下占位符：

| 占位符 | 替换为 |
|---|---|
| `[Project]` | 项目名称（`FApp::GetProjectName()`） |
| `[Platform]` | 平台名称（如 `Win64`） |
| `[DumpTime]` | dump 时间戳 |
| `[DumpType]` | dump 类型 |

### 进阶用法

上传过程的内部实现细节：

- **并发上传** — 默认同时发送 4 个 HTTP 请求（`kOverlappedRequests = 4`）
- **压缩传输** — 支持对匹配的文件进行压缩后再上传，压缩算法和匹配规则由 `FDumpParameters` 控制
- **编辑器集成** — 在编辑器中会显示 Slate 进度通知条，桌面平台上传完成后会自动打开浏览器访问 dump URL
- **自动清理** — 上传成功后自动删除本地 dump 目录；失败时保留目录并输出日志
- **串行队列** — 多次 dump 的上传请求会排队，一次只执行一个上传任务

## Demo 示例

此插件没有独立的 Demo，它作为 `DumpGPU` 命令的后端服务运行。

启用步骤：

1. 在编辑器中启用插件（默认已启用）
2. 配置 `UploadURLPattern`（见上方配置方式）
3. 在控制台执行 `DumpGPU` 命令触发渲染 dump
4. dump 完成后自动上传到配置的服务器

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础模块（公共依赖） |
| `RenderCore` | 提供 `IDumpGPUUploadServiceProvider` 接口和 `DumpGPU` 命令 |
| `Json` | 解析 dump service 的 JSON 参数文件 |
| `HTTP` | 执行 HTTP PUT 上传请求 |
| `Slate` | 编辑器中显示上传进度通知（仅 Editor 构建） |

### 构建限制

- **不支持 Server 目标** — `TargetDenyList: ["Server"]`
- **不支持 Shipping 配置** — `TargetConfigurationDenyList: ["Shipping"]`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2024-10-22 | `98a8e0e0` | 移除 UE 5.2 的 `#include` 顺序兼容宏 |
| 2024-01-19 | `f0294685` | 将 `bool` 参数的容器 resize 改为 `EAllowShrinking` 枚举 |
| 2023-02-21 | `8676f608` | 将 `DumpGPU.h` 移到 Public 目录以便此插件正确访问 |

三次提交均为代码维护/重构，没有功能性变更。

### 维护评价

- 创建于 2022 年 3 月，已约 4 年历史，属于 🆕 范围
- **实验性插件** — `.uplugin` 中 `IsExperimentalVersion: true`
- 近两年无功能性更新，三次 commit 均为编译兼容性修复
- 插件功能简单（仅 4 个源文件），代码稳定，不太需要频繁更新
- 核心逻辑完整可用，但标记为实验性意味着 Epic 可能会在未来调整或移除
- **不推荐用于生产环境的自动化流水线**，适合内部团队调试使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/DumpGPUServices)
- [DumpGPU 接口（RenderCore）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/RenderCore/Public/DumpGPU.h)
- [DumpGPU 实现（RenderCore）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/RenderCore/Private/DumpGPU.cpp)
