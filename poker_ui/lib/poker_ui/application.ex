defmodule PokerUi.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      PokerUiWeb.Telemetry,
      PokerUi.Repo,
      {DNSCluster, query: Application.get_env(:poker_ui, :dns_cluster_query) || :ignore},
      {Phoenix.PubSub, name: PokerUi.PubSub},
      # Start a worker by calling: PokerUi.Worker.start_link(arg)
      # {PokerUi.Worker, arg},
      # Start to serve requests, typically the last entry
      PokerUiWeb.Endpoint
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: PokerUi.Supervisor]
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    PokerUiWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
