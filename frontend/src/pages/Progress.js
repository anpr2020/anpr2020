import React from "react";

export default class Progress extends React.Component {
  constructor(props) {
		super(props);
    this.state = {
      progressState: null,
      progressInfo: null,
    };
  }

  getTaskInfo = async (data) => {
    return await (
      await fetch(window.djangoUrls.Progress, {
				method: "POST",
        body: JSON.stringify(data),
      })
    ).json();
  };

	componentDidMount(){
		const { progressState } = this.state;
		const {id} = this.props.match.params;
		
		const liveUpdates = () => {
			this.getTaskInfo({'task_id': id}).then(res => {
				console.log(res.json());
				setTimeout(liveUpdates(), 1000);
			})
		};

		liveUpdates();
	}

  render() {
    return (
			<div></div>
		);
  }
}
