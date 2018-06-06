import React from 'react';
import './DatasetCard.css';

function DatasetCard(props) {
    return (
		<div className="dataset-panel">
			 <div className="dataset-heading">{ props.dataset.fullName }</div>
			 <div className="dataset-body">
                {props.dataset.hasImage && <img src="/api/datasets/{props.dataset.shortName}/logo" className="dataset-logo" alt='{ props.dataset.shortName } logo' /> }
                {props.dataset.future && <div className='future-blurb'>This version will become public at { props.dataset.version.availableFrom }.</div> }
				 <div dangerouslySetInnerHTML={{ __html: props.dataset.version.description }} />
			 </div>
			 <div className="dataset-links">
				 <li><a href="{ props.dataset.urlbase }">More information</a></li>
				 <li><a href="{ props.dataset.urlbase + '/beacon' }">Beacon</a></li>
				 <li><a href="{ props.dataset.urlbase + '/browser' }">Graphical Browser</a></li>
			 </div>
		</div>
    )
}

export default DatasetCard;
