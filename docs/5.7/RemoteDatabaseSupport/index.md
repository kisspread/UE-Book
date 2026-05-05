# Remote Database Support

> Remote Database Support

| 属性 | 值 |
|---|---|
| 分类 | Database |
| 默认启用 | ❌ No |
| 包含内容 | ❌ No |
| 模块 | RemoteDatabaseSupport (Runtime) |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/RemoteDatabaseSupport) | |

## 用途

RemoteDatabaseSupport 为**不原生支持数据库的平台**提供远程数据库代理连接能力。它通过 TCP Socket 连接到一个运行在 PC 上的 **DB Proxy 服务**，将 SQL 命令以 XML 格式发送给代理，由代理转发给实际的数据库（如 SQLite、MySQL 等）。

这个 plugin 存在的历史原因是：早期主机平台（如 PS3/Xbox 360）没有原生数据库驱动，但开发过程中需要访问数据库（例如读取配置数据、存档验证等）。通过远程代理的方式，游戏可以在受限平台上透明地执行数据库操作。

从源码可以看到，通信协议使用网络字节序（`NETWORK_ORDER_TCHARARRAY`），并有 `PS3`/`Xenon` 时代的注释残留，证实了这一设计动机。

> **注意**：此 plugin 默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你在开发主机平台游戏，该平台没有原生数据库驱动 → 用 RemoteDatabaseSupport 通过代理访问数据库
- 你需要在开发/测试阶段从游戏客户端远程查询数据库 → 用 RemoteDatabaseConnection 连接到 DB Proxy
- 你正在移植一个使用 DatabaseSupport 的项目到不支持本地数据库的平台 → 切换到 RemoteDatabaseConnection 保持相同 API

## 蓝图用法

此 plugin **没有暴露任何蓝图节点**。所有类都是纯 C++ 类，没有 `UCLASS`、`UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteDatabaseConnection.h"
```

### 核心类

#### FRemoteDatabaseConnection

继承自 `FDataBaseConnection`（来自 DatabaseSupport 模块），通过 TCP Socket 连接到远程 DB Proxy。

| 方法 | 说明 |
|---|---|
| `Open(ConnectionString, RemoteConnectionIP, RemoteConnectionStringOverride)` | 连接到指定 IP 的 DB Proxy（端口 10500） |
| `Close()` | 关闭 Socket 连接 |
| `Execute(CommandString)` | 执行 SQL 命令（不返回结果） |
| `Execute(CommandString, RecordSet&)` | 执行 SQL 命令并返回结果集 |
| `SetConnectionString(ConnectionString)` | 在代理端设置连接字符串 |

#### FRemoteDataBaseRecordSet

继承自 `FDataBaseRecordSet`，代表从远程代理获取的查询结果集。

| 方法 | 说明 |
|---|---|
| `GetString(Column)` | 获取当前行指定列的字符串值 |
| `GetInt(Column)` | 获取当前行指定列的整数值 |
| `GetFloat(Column)` | 获取当前行指定列的浮点值 |

### 基本用法

```cpp
// 来源: RemoteDatabaseConnection.h + RemoteDatabaseConnection.cpp

#include "RemoteDatabaseConnection.h"

// 1. 创建连接
FRemoteDatabaseConnection Connection;

// 2. 打开连接：参数为连接字符串、代理 IP、覆盖连接字符串
bool bConnected = Connection.Open(
    TEXT("Driver={SQLite3};Database=mydb"),  // 连接字符串（传给代理）
    TEXT("192.168.1.100"),                    // DB Proxy 所在机器的 IP
    TEXT("Server=localhost;Database=game")    // 覆盖代理端使用的连接字符串
);

if (bConnected)
{
    // 3. 执行带结果集的查询
    FDataBaseRecordSet* RecordSet = nullptr;
    if (Connection.Execute(TEXT("SELECT * FROM Players"), RecordSet))
    {
        // 4. 遍历结果集
        while (RecordSet && !RecordSet->IsAtEnd())
        {
            FString Name = RecordSet->GetString(TEXT("Name"));
            int32 Score = RecordSet->GetInt(TEXT("Score"));
            // ... 处理数据
            RecordSet->MoveToNext();
        }
        
        // 5. 清理结果集（析构时会通知代理释放资源）
        delete RecordSet;
    }

    // 6. 执行无返回值的命令
    Connection.Execute(TEXT("INSERT INTO Logs VALUES ('test', 123)"));

    // 7. 关闭连接
    Connection.Close();
}
```

### 进阶用法

```cpp
// 动态切换代理端的数据库连接
FRemoteDatabaseConnection Connection;
Connection.Open(TEXT(""), TEXT("10.0.0.5"), nullptr);

// 通过 SetConnectionString 在代理端切换数据库
Connection.SetConnectionString(TEXT("Server=10.0.0.5;Database=production"));
Connection.Execute(TEXT("SELECT COUNT(*) FROM Users"), RecordSet);

Connection.SetConnectionString(TEXT("Server=10.0.0.5;Database=analytics"));
Connection.Execute(TEXT("SELECT * FROM Events WHERE date > '2024-01-01'"), RecordSet);
```

**注意**：`SetConnectionString` 并不改变本地连接，而是通过 Socket 命令让远程代理切换其内部的数据库连接。

## 通信协议

插件与 DB Proxy 之间使用基于 XML 的文本协议，所有数据通过网络字节序传输：

```
# 执行命令（无结果）
<command results="false">SQL_STATEMENT</command>

# 执行命令（有结果）
<command results="true">SQL_STATEMENT</command>
→ 返回: int32 ResultID

# 设置连接字符串
<connectionString>CONN_STRING</connectionString>

# 结果集操作
<movetofirst resultset="0"/>
<movetonext resultset="0"/>
<isatend resultset="0"/>
→ 返回: bool

<getstring resultset="0">COLUMN_NAME</getstring>
→ 返回: int32 Length + TCHAR[] Data

<getint resultset="0">COLUMN_NAME</getint>
→ 返回: int32 Value

<getfloat resultset="0">COLUMN_NAME</getfloat>
→ 返回: int32 (as float bits)

# 释放结果集
<closeresultset resultset="0"/>
```

## Demo 示例

### 最小示例：查询远程数据库

```cpp
// MyDatabaseActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyDatabaseActor.generated.h"

UCLASS()
class AMyDatabaseActor : public AActor
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable)
    void QueryRemoteDB();
};

// MyDatabaseActor.cpp
#include "MyDatabaseActor.h"
#include "RemoteDatabaseConnection.h"

void AMyDatabaseActor::QueryRemoteDB()
{
    FRemoteDatabaseConnection* Conn = new FRemoteDatabaseConnection();
    
    if (Conn->Open(TEXT(""), TEXT("192.168.1.100"), TEXT("Driver=MySQL;Server=db.local")))
    {
        FDataBaseRecordSet* RS = nullptr;
        if (Conn->Execute(TEXT("SELECT name, score FROM leaderboard LIMIT 10"), RS))
        {
            while (RS && !RS->IsAtEnd())
            {
                UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %d"),
                    *RS->GetString(TEXT("name")),
                    RS->GetInt(TEXT("score")));
                RS->MoveToNext();
            }
            delete RS;
        }
        Conn->Close();
    }
    delete Conn;
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "DatabaseSupport",
    "RemoteDatabaseSupport"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `DatabaseSupport` | 提供 `FDataBaseConnection` 和 `FDataBaseRecordSet` 基类 |
| `Sockets` | 提供 TCP Socket 通信能力（私有依赖） |

Plugin 级别还依赖 `DatabaseSupport` plugin（在 .uplugin 的 Plugins 字段中声明）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-04-02 | `f0ec1829e3a8` | PR #8660: Fix `bool ExecuteDBProxyCommand()` | 修复了 `ExecuteDBProxyCommand` 函数的返回值问题 |
| 2023-01-16 | `bbc37aa2f5e6` | Another batch IWYU updates to reduce number of includes | IWYU（Include What You Use）清理，无功能变更 |
| 2022-10-21 | `610c467639c8` | Update vendor links to use secure protocol | 将 HTTP 链接更新为 HTTPS，无功能变更 |

### 维护评价

- **创建时间**：2019-01-10，已有 7 年历史
- **更新频率**：最近 3 次 commit 均为维护性更新（编译修复、IWYU、URL 更新），无功能性更新
- **活跃度**：⚠️ 维护不活跃 — 最后一次实质性功能更新远早于 2022 年
- **已知限制**：
  - 硬编码端口 10500，无法配置
  - 不支持加密连接（`RequiresEncryptedPackets()` 为 true 时直接失败）
  - `GetString` 缓冲区固定 2048 TCHAR，超长字符串会被截断
  - 通信协议是自定义 XML 格式，需要配合特定的 DB Proxy 工具使用
- **推荐程度**：⚠️ 仅在特定场景下使用。此 plugin 是为了解决已不存在的历史问题（老主机平台无数据库驱动）。现代平台（PS5/Xbox Series/Switch）通常有原生数据库支持，建议直接使用 DatabaseSupport plugin 的平台原生实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/RemoteDatabaseSupport)
- [DatabaseSupport plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/DatabaseSupport)（基类 plugin）
