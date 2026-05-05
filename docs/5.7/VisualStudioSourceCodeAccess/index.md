# Visual Studio Integration

> Allows access to source code in Visual Studio.

| 属性 | 值 |
|---|---|
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 否 |
| 模块 | VisualStudioSourceCodeAccess (UncookedOnly) |
| 创建时间 | 2014-04-23 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/VisualStudioSourceCodeAccess) | |

## 用途

这个 Plugin 实现了 UE5 与 Visual Studio 之间的深度集成。它不是简单地"打开文件"，而是作为 UE5 的 **源码访问器 (Source Code Accessifier)**，负责：

1. **自动检测已安装的 Visual Studio 版本**（通过 Visual Studio Setup API，最低支持 VS 2022）
2. **在 UE 编辑器中一键跳转到 VS 中的源码文件和行号**——双击编译错误、点击蓝图中的 C++ 节点等操作会自动打开 VS 并定位
3. **通过 COM DTE 接口与运行中的 VS 实例通信**——无需重新启动 VS，直接在同一窗口中打开文件、跳转行号、保存文档
4. **在 C++ 重编译前自动保存 VS 中的所有打开文档**，防止内容丢失
5. **智能管理多个 VS 实例和多个 .sln 文件**——能根据请求打开的文件，推测应该使用哪个解决方案
6. **延迟请求队列**——如果 VS 还没启动完成，文件打开请求会排队等待

简单说：**它让你在 UE 编辑器里点一下，就能在 VS 中打开对应的代码行。**

## 使用场景

- 你在 UE 编辑器中看到编译错误，双击错误信息 → 自动在 VS 中打开对应文件并定位到出错行
- 你在蓝图中右键 C++ 节点选择 "Go to Definition" → 在 VS 中打开对应源码
- 你在 UE 编辑器中触发 C++ 编译 → VS 中已修改但未保存的文件会自动保存，避免冲突
- 你安装了 VS 2022 和 VS 2026 Preview → Plugin 会根据 .sln 版本自动选择正确的 VS 实例

## 编辑器设置

该 Plugin 在 UE 编辑器中提供了设置面板，路径：**Editor → Plugins → Visual Studio**。

### 配置项

| 设置项 | 类型 | 说明 |
|---|---|---|
| `Direct Unreal Project Support` (`bUproject`) | bool | 直接用 VS 打开 `.uproject` 文件，而不是生成的 `.sln` 解决方案 |
| `Prefer Preview Releases` (`bPreview`) | bool | 优先使用 Visual Studio 的 Preview 预览版 |

设置存储在 `EditorSettings` 配置文件中（`config=EditorSettings`）。

## 蓝图用法

本 Plugin **不暴露任何蓝图接口**。它是纯编辑器/工具层面的集成，所有功能在编辑器 UI 中自动工作，无需蓝图调用。

## C++ 用法

本 Plugin 的主要用户是引擎内部的源码访问系统（`SourceCodeAccess` 模块）。普通游戏项目代码一般不会直接调用此 Plugin。以下是引擎内部的接口说明。

### 头文件引入

```cpp
#include "ISourceCodeAccessor.h"
```

### 核心接口：ISourceCodeAccessor

该 Plugin 的核心类 `FVisualStudioSourceCodeAccessor` 实现了 `ISourceCodeAccessor` 接口。以下是该接口的关键方法：

```cpp
// 检查 VS 是否可用
bool CanAccessSourceCode() const;

// 打开 .sln 解决方案
bool OpenSolution();

// 在指定行号打开文件
bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0);

// 打开多个源码文件
bool OpenSourceFiles(const TArray<FString>& AbsoluteSourcePaths);

// 保存 VS 中所有打开的文档
bool SaveAllOpenDocuments() const;

// 添加源码文件到项目
bool AddSourceFiles(const TArray<FString>& AbsoluteSourcePaths, const TArray<FString>& AvailableModules);
```

### 通过模块系统访问

```cpp
// 获取源码访问模块
ISourceCodeAccessModule& SourceCodeAccessModule = 
    FModuleManager::LoadModuleChecked<ISourceCodeAccessModule>("SourceCodeAccess");

// 获取当前激活的源码访问器（如果 VS 是当前选择的 IDE，返回的就是 VS 访问器）
ISourceCodeAccessor& Accessor = SourceCodeAccessModule.GetAccessor();

// 在 VS 中打开文件并跳转到指定行
Accessor.OpenFileAtLine(TEXT("/Game/Source/MyClass.cpp"), 42, 0);
```

### VS 版本检测机制

Plugin 通过 Visual Studio Setup API（COM 接口 `ISetupConfiguration`）扫描系统中安装的所有 VS 实例：

```cpp
// 最低支持 VS 2022 (版本号 17)
static constexpr int32 MinimumVisualStudioVersion = 17;

// 使用 Setup API 枚举所有安装
void AddVisualStudioVersionUsingVisualStudioSetupAPI(const int MinimumVersionNumber);

// 根据 .sln 文件版本号和设置进行优先级排序
TArray<VisualStudioLocation> GetPrioritizedVisualStudioVersions(const FString& InSolution) const;
```

排序逻辑考虑：
- .sln 文件中声明的 VS 版本号
- 设置中的 `bPreview` 偏好
- 当前编译器版本（`_MSC_VER`）

### DTE 通信机制

当 `WITH_VISUALSTUDIO_DTE` 启用时，Plugin 通过 COM 的 Running Object Table (ROT) 找到运行中的 VS 实例，使用 `EnvDTE::_DTE` 接口进行通信：

```cpp
// 通过 DTE 打开文件（在已运行的 VS 中）
bool OpenVisualStudioFilesInternalViaDTE(const TArray<FileOpenRequest>& Requests, bool& bWasDeferred);

// 通过 DTE 打开解决方案
bool OpenVisualStudioSolutionViaDTE();
```

如果 VS 尚未运行或被阻塞（模态对话框），请求会被放入延迟队列，等到 VS 就绪后自动处理。

### 非 DTE 降级方案

当 DTE 不可用时（如 VS Express 版），Plugin 会回退到直接进程启动方式：

```cpp
// 直接启动 VS 进程
bool OpenVisualStudioSolutionViaProcess();
bool OpenVisualStudioFilesInternalViaProcess(const TArray<FileOpenRequest>& Requests);
```

## 模块依赖

从 `VisualStudioSourceCodeAccess.Build.cs` 提取的依赖关系：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `SourceCodeAccess` | 源码访问器抽象接口层 |
| `DesktopPlatform` | 桌面平台功能（文件对话框等） |
| `Projects` | 项目描述和管理 |
| `Json` | JSON 序列化（用于解析 VS 配置） |
| `VisualStudioSetup` | VS Setup API 封装（第三方位于 `Source/ThirdParty/VisualStudioSetup/`） |
| `VisualStudioDTE` | VS DTE COM 接口封装 |
| `HotReload` | （仅编辑器）热重编译回调，在编译前自动保存 VS 文档 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-11 | `c4481b3` | 实验性 VS 2026 支持，移除已废弃的 VS Mac 项目生成器 |
| 2025-06-17 | `a2f48da` | 修复引擎范围的循环头文件包含 |
| 2025-04-09 | `fd22a8b` | 新增 `bUproject`（直接打开 .uproject）和 `bPreview`（优先 Preview 版）设置项 |

### 维护评价

- **创建时间**: 2014-04-23，是 UE4 时代最早的 Plugin 之一
- **更新频率**: 2025 年内有 3 次实质性更新，包括新功能和新 VS 版本支持
- **维护状态**: ✅ **活跃维护** — Epic 持续跟踪新版 VS 发布
- **已知限制**:
  - 仅支持 Windows (Win64)
  - 仅在 `UncookedOnly`（编辑器/开发工具）阶段加载
  - 最低支持 VS 2022，不支持旧版 VS
  - `.uplugin` 中 `SupportedPrograms` 包含 `UnrealFrontend` 和 `UnrealInsights`
- **推荐使用**: ✅ **强烈推荐** — 如果你使用 Visual Studio 作为 UE5 的 C++ IDE，这是必备 Plugin（默认已启用）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/VisualStudioSourceCodeAccess)
- [VisualStudioSetup 第三方库](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/VisualStudioSourceCodeAccess/Source/ThirdParty/VisualStudioSetup)
